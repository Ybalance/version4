import openai
import base64
import os
import json
import re

# API Configuration
# Note: In a real production environment, use environment variables (os.getenv)
# For this specific deployment, we configure it here as requested.
API_KEY = "sk-jsalomnmtzopeskqspwkmqorzebeslgzlfwwobaoqmopsxmm"
BASE_URL = "https://api.siliconflow.cn/v1"

def generate_capsule_details(image_bytes: bytes, user_description: str = ""):
    """
    Calls the SiliconFlow API (Qwen2.5-VL) to analyze an image.
    Returns a JSON with title, description, and tags.
    """
    
    # Initialize OpenAI client with SiliconFlow config
    client = openai.OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )

    try:
        # Encode image to base64
        encoded_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # Construct the prompt
        base_prompt = "分析这张图片"
        if user_description:
            base_prompt += f"，结合用户提供的描述：“{user_description}”"
            
        prompt_text = (
            f"{base_prompt}，生成一个温馨、充满诗意的记忆胶囊标题（10字以内）和一段简短的感悟描述（50字以内），以及3个相关标签。"
            "请严格按照以下JSON格式返回，不要包含任何markdown格式或额外文本："
            "{\"title\": \"...\", \"description\": \"...\", \"tags\": \"tag1, tag2, tag3\"}"
        )

        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-VL-72B-Instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            }
                        },
                        {
                            "type": "text", 
                            "text": prompt_text
                        }
                    ]
                }
            ],
            temperature=0.7,
            max_tokens=512
        )
        
        content = response.choices[0].message.content.strip()
        print(f"AI Raw Response: {content}")
        
        # Clean up potential markdown code blocks (```json ... ```)
        if content.startswith("```"):
            content = re.sub(r"^```json\s*", "", content)
            content = re.sub(r"^```\s*", "", content)
            content = re.sub(r"\s*```$", "", content)
            
        return json.loads(content)

    except Exception as e:
        print(f"AI API Error: {e}")
        # Fallback to mock response if API fails
        return {
            "title": "时光的印记",
            "description": "（AI生成暂时不可用）在这静谧的一刻，光影交错，仿佛诉说着一段不为人知的往事。",
            "tags": "温馨, 记忆, 瞬间"
        }
