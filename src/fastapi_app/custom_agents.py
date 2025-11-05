# """
# custom_agents.py

# Module for creating motivational interviewing agent.
# """

import os
import pandas as pd
from pydantic import BaseModel
from openai import AsyncAzureOpenAI, BadRequestError
from agents import (
    AsyncOpenAI, Agent, Runner, 
    OpenAIChatCompletionsModel, set_tracing_disabled,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    TResponseInputItem,
    input_guardrail
)
from dotenv import load_dotenv
from fastapi_app.mi_prompts import (
    mi_prompt, 
    harm_prompt, harm_response, 
    mi_check_prompt, mi_check_response
)
from fastapi_app.sensing_prompts import sensing_tool_description
from fastapi import HTTPException

load_dotenv() 

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
model_name = "gpt-4o"
deployment = "gpt-4o"
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = "2024-12-01-preview"

client = AsyncAzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
    )

model = OpenAIChatCompletionsModel(
    model=deployment,
    openai_client=client,
)

# Create harm guardrail
class HarmOutput(BaseModel):
    is_harm: bool
    reasoning: str

harm_agent = Agent(
    name="Harm Agent",
    instructions=harm_prompt,
    model=model,
    output_type=HarmOutput
)

@input_guardrail
async def harm_guardrail(
    ctx: RunContextWrapper[None], 
    agent: Agent, 
    messages: str | list[TResponseInputItem]
):
    result = await Runner.run(harm_agent, messages, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=harm_response, 
        tripwire_triggered=result.final_output.is_harm,
    )

# Create mi_check_guardrail
class MICheckOutput(BaseModel):
    is_not_mi: bool
    reasoning: str

mi_check_agent = Agent(
    name="MI Check Agent",
    instructions=mi_check_prompt,
    model=model,
    output_type=MICheckOutput
)

@input_guardrail
async def mi_check_guardrail(
    ctx: RunContextWrapper[None], 
    agent: Agent, 
    messages: str | list[TResponseInputItem]
):
    result = await Runner.run(
        mi_check_agent, messages, context=ctx.context
    )

    return GuardrailFunctionOutput(
        output_info=mi_check_response, 
        tripwire_triggered=result.final_output.is_not_mi,
    )



def create_sensing_prompt(
    prompt, 
    step_count_prompt, sleep_duration_prompt, hrv_prompt,
    step_data, sleep_data, hrv_data
):
    """_summary_

    prompt: <str>, the template prompt
    step_count_prompt: <str>, the step count prompt
    sleep_duration_prompt: <str>, the sleep duration prompt
    hrv_prompt: <str>, the hrv prompt
    step_data: pd.DataFrame, the step data
    sleep_data: pd.DataFrame, the sleep data
    hrv_data: pd.DataFrame, the hrv data
    
    return: <str>, the prompt with the templated data
    """
    # Add step data
    if pd.isnull(step_data).sum().sum() == 0:
        step_prompt_temp = step_count_prompt.replace(
            '[INSERT STEP COUNT DATA]', step_data.to_markdown()
        )
        prompt += step_prompt_temp
    
    if pd.isnull(sleep_data).sum().sum() == 0:
        sleep_duration_prompt_temp = sleep_duration_prompt.replace(
            '[INSERT SLEEP DURATION DATA]', sleep_data.to_markdown()
        )
        prompt += sleep_duration_prompt_temp

    if pd.isnull(hrv_data).sum().sum() == 0:
        hrv_prompt_temp = hrv_prompt.replace(
            '[INSERT HRV DATA]', hrv_data.to_markdown()
        )
        prompt += hrv_prompt_temp

    print(prompt)
    
    return prompt

# Motivational Interviewing Agent
def create_agent(
    use_harm_guardrail=True,
    use_mi_check_guardrail=True,
    use_sensing_agent=False,
    sensing_prompt=None
):
    """
    Create the agent.

    use_harm_guardrail: <bool> Whether to use the 
                          harm_guardrail
                          defaults to True
    use_mi_check_guardrail: Whether to use the 
                            MI check guardrail
                            defaults to True
    use_sensing_agent: Whether to use the sensing agent
                       defaults to False
    sensing_prompt: <str>, the sensing prompt
    """
    # Check guardrails
    guardrails = []
    if use_harm_guardrail:
        guardrails.append(harm_guardrail)
    if use_mi_check_guardrail:
        guardrails.append(mi_check_guardrail)

    # Check sensing agent
    tools = []
    if use_sensing_agent:
        # Create sensing agent
        sensing_agent = Agent(
            name="Sensing Agent",
            instructions=sensing_prompt,
            model=model,
        )
        # Make as a tool
        tools.append(
            sensing_agent.as_tool(
                tool_name="sensing_expert",
                tool_description=sensing_tool_description,
            )
        )

    # Create agent
    agent = Agent(
        name="MI Agent",
        instructions=mi_prompt,
        model=model,
        input_guardrails=guardrails,
        tools=tools
    )
    return agent



REQUIRED_FIELDS = [
    "user_id",
    "message",
    "use_harm_guardrail",
    "use_mi_check_guardrail",
    "use_sensing_agent"
]


async def getResponse(chat_request: dict):
    """
    Calls the agent with the messages field.
    Returns response or raises exceptions.
    """
    print(chat_request)
    # Validate required fields
    missing_fields = [f for f in REQUIRED_FIELDS if f not in chat_request]
    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )

    # Extract data from chat_request
    messages = chat_request.get("message")
    use_harm_guardrail = chat_request.get("use_harm_guardrail", True)
    use_mi_check_guardrail = chat_request.get("use_mi_check_guardrail", True)
    use_sensing_agent = chat_request.get("use_sensing_agent", False)
    sensing_prompt = chat_request.get("sensing_prompt")

    # Create the agent
    agent = create_agent(
        use_harm_guardrail=use_harm_guardrail,
        use_mi_check_guardrail=use_mi_check_guardrail,
        use_sensing_agent=use_sensing_agent,
        sensing_prompt=sensing_prompt
    )

    # Run the agent
    result = await Runner.run(
        starting_agent=agent,
        input=messages
    )

    return result.final_output

async def get_agent_response(chat_request):
    print("Validating chat request:")
    try:
        response = await getResponse(chat_request)
    except InputGuardrailTripwireTriggered as e:
        response = e.guardrail_result.output.output_info
    except BadRequestError:
        response = harm_response
    except HTTPException as e:
        return {"error": e.detail}
    return response


