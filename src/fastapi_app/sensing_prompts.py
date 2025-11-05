"""
sensing_prompts.py

The  prompts for the sensing-based chatbots.
"""

sensing_prompt = """
# Your Task
1. You are observing a Motivational Interviewing counselling session between a counsellor and a user.

2. Your job is to contextualize the conversation with the data described below. It is important to consider:
    1. How the data relates to the broader circumstances described in the conversation.
    2. It is helpful to focus on long-term trends in the data rather than short-term variations.
    3. Do not state specific numbers. State general trends.

3. Here are some ways you can use the data.
    1. You can present it to the user to help them reflect upon how their behavioral or physiological data may affect thier mental health.
    2. You can use it to help the user learn more about their behavior and physiology.
    3. You can use the data to help the user track a behavior changes they are interested in doing.
    4. You can use the data to help the user identify a possible behavior or physiological signal they may be interested in changing.

"""

step_count_prompt = """
 
# Step Count Data

1. The table has two columns: "date" and "value".
2. The "date" column contains dates describing the day the data was collected.
3. The "value" column describes the number of steps the user took on the date described in the first column.

[INSERT STEP COUNT DATA]

"""

sleep_duration_prompt = """

# Sleep Duration Data

1. The table has two columns: "date" and "value".
2. The "date" column contains dates describing the day the data was collected.
3. The "value" column describes the number of hours the user slept on the date described in the first column.

[INSERT SLEEP DURATION DATA]

"""

hrv_prompt = """

# Heart Rate Variability Data

1. The table has two columns: "date" and "value".
2. The "date" column contains dates describing the day the data was collected.
3. The "value" column describes the average heart rate variability collected on the date described in the first column.
4. Heart rate variability is a physiological signal controlled by the autonomic nervous system.
5. Lower heart rate variability may indicate that the user is experiencing more physiological stress.
6. Higher heart rate variability may indicate that the user is experiencing a healthy amount of stress.
7. Heart rate variability is a relative signal, so it is helpful to consider relative trends over absolute numbers.
8. The user may not know what heart rate variability is, so it may be important to explain this data as the physiological response to stress.

[INSERT HRV DATA]

"""

sensing_tool_description = """
This tool can give you data on the user's sleep duration and step counts to help you with motivational interviewing.
"""