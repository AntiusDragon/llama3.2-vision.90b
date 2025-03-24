import ollama

response = ollama.chat(
    model='llama3.2-vision:90b',
    messages=[{
        'role': 'user',
        'content': 'Šiame image1 yra Japoniškas raštas, Pateik orginalia teksta ir Lietuviu kalba.',
        'images': ['image1.png']
    }]
)

print(response)