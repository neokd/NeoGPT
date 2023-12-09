from sentence_transformers import SentenceTransformer, util

# TASK AND RESPONSE PROMPTS
TASK_PROMPTS = {
    "rag": "You are a helpful assistant, you will use the provided context to answer user questions. Read the given context before answering questions and think step by step. If you can not answer a user  question based on the provided context, inform the user. Do not use any other information for answering user.",
    "summarization": "Your task is to summarize the text I give you in up to seven concise bullet points and start with a short, high-quality summary. Pick a suitable emoji for every bullet point. Your response should be in {{SELECTED_LANGUAGE}}. If the provided URL is functional and not a YouTube video, use the text from the {{URL}}. However, if the URL is not functional or is a YouTube video, use the following text: {{CONTENT}}.",
}


def hyper_prompt(model_type: str = "mistral", user_input: str = ""):
    try:
        model = SentenceTransformer(
            "/Users/kuldeep/Project/NeoGPT/models/sentence-transformers_all-MiniLM-L12-v2/"
        )
    except Exception as e:
        print(e)

    user_embedding = model.encode(user_input, convert_to_tensor=True)

    # Calculate similarity scores between user input and each task's prompt
    similarity_scores = {}
    for task, prompt in TASK_PROMPTS.items():
        task_embedding = model.encode(prompt, convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(user_embedding, task_embedding).item()
        similarity_scores[task] = similarity

    # Choose the task with the highest similarity score
    chosen_task = max(similarity_scores, key=similarity_scores.get)
    chosen_prompt = TASK_PROMPTS[chosen_task]
    print(chosen_prompt)
    return chosen_prompt


if __name__ == "__main__":
    hyper_prompt()
