from google import genai

client = genai.Client(api_key="AIzaSyAnO7kOcOUsOBhjw9PbsIU8s1qCWkUMWck")
def chat_ai(user_input):
    response = client.models.generate_content(
    model="gemini-2.0-flash", contents=user_input)
    return response.text
    
