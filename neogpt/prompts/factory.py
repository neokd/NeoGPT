def mistral_pt(messages):
    """
    This function generates the prompt for Mistral model with special tokens.
    """
    return custom_prompt(
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
        bos_token="",
        eos_token="",
    )


def custom_prompt(
    role_dict: dict,
    messages: list,
    initial_prompt_value: str = "",
    final_prompt_value: str = "",
    bos_token: str = "",
    eos_token: str = "",
):
    formatted_messages = []
    prompt = bos_token + initial_prompt_value
    for message in messages:
        role = message["role"]

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

        formatted_message = pre_message_str + message["content"] + post_message_str
        formatted_messages.append({"role": role, "content": formatted_message})

    return formatted_messages


def prompt_factory(model, messages):
    original_model = model.lower().strip()
    if "mistral" in original_model:
        prompt = mistral_pt(messages)
    elif "phi3" in original_model:
        prompt = messages
    else:
        prompt = messages
    return prompt
