from pyngrok import ngrok

# เปิด tunnel ที่พอร์ต 5000
public_url = ngrok.connect(5000)
print("Public URL:", public_url)
