def mistral_pt(messages):
    """
    This function is used to generate the prompt for Mistral model.
    """
    prompt = custom_prompt(
        initial_prompt_value="<s>",
        role_dict={
            "system": {
                "pre_message": "[INST] \n",
                "post_message": " [/INST]\n",
            },
            "user": {"pre_message": "[INST] ", "post_message": " [/INST]\n"},
            "assistant": {"pre_message": " ", "post_message": " "},
        },
        final_prompt_value="",
        messages=messages,
    )
    return prompt


def custom_prompt(
    role_dict: dict,
    messages: list,
    initial_prompt_value: str = "",
    final_prompt_value: str = "",
    bos_token: str = "",
    eos_token: str = "",
):
    prompt = bos_token + initial_prompt_value
    bos_open = True

    for message in messages:
        role = message["role"]

        if role in ["system", "human"] and not bos_open:
            prompt += bos_token
            bos_open = True

        pre_message_str = (
            role_dict[role]["pre_message"]
            if role in role_dict and "pre_message" in role_dict[role]
            else ""
        )
        post_message_str = (
            role_dict[role]["post_message"]
            if role in role_dict and "post_message" in role_dict[role]
            else ""
        )

        prompt += pre_message_str + message["content"] + post_message_str

        if role == "assistant":
            prompt += eos_token
            bos_open = False

    prompt += final_prompt_value
    return prompt


def convert_to_open_ai_message(messages):
    new_messages = []

    for message in messages:
        new_message = {
            "role": message["role"],
            "content": message["content"],
        }
        new_messages.append(new_message)


def prompt_factory(model, messages):
    original_model = model.lower()
    # print(original_model)
    if "mistral" in original_model:
        prompt = mistral_pt(messages)
    return prompt.split()
