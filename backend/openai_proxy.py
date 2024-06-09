from gpt35_keys import openai_url, openai_key
import requests
import json
def gpt35(inp, temperature=0.01, max_tokens=512):
    API_URL = openai_url
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai_key
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": inp}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    return requests.post(API_URL, headers=headers, data=json.dumps(data)).json()



import random
import time
# define a retry decorator
def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 10,
    DEBUG=False
):
    """Retry a function with exponential backoff."""

    def wrapper(*args, **kwargs):
        # Initialize variables
        num_retries = 0
        delay = initial_delay

        # Loop until a successful response or max_retries is hit or an exception is raised
        while True:
            try:
                rst = func(*args, **kwargs)
                if 'error' not in rst:
                    return rst
                else:
                    raise Exception(rst['error'])
                return rst
            # Retry on specified errors
            except Exception as e:
                if DEBUG:
                    print("[ERROR in OpenAI]: ", e)
                # Increment retries
                num_retries += 1

                # Check if max retries has been reached
                if num_retries > max_retries:
                    raise Exception(
                        f"Maximum number of retries ({max_retries}) exceeded."
                    )

                # Increment the delay
                delay *= exponential_base * (1 + jitter * random.random())

                # Sleep for the delay
                time.sleep(delay)

            # Raise exceptions for any errors not specified
            # except Exception as e:
            #     raise e
    return wrapper

@retry_with_exponential_backoff
def completions_with_backoff(inp, temperature=0.3):
    return gpt35(inp, temperature=temperature)



if __name__ == "__main__":
    # gpt35("Hello!")
    import time
    for i in range(10):
        start = time.time()
        print(i)
        output = completions_with_backoff("Hello!", temperature=0.8)
        print("output:\t", output)
        print("output text:\t", output['choices'][0]['message']['content'])
        print("consuming:\t", time.time() - start)