import requests
import time
from bs4 import BeautifulSoup

# Configuración
TELEGRAM_TOKEN = '7579763061:AAG4vkaNm1BGfqH5rLue1Piq0_0GGRVNVDY'  # Sustituye con tu token de Telegram
CHAT_ID = '-1001878386285'  # ID del grupo (debe ser negativo)
BLOG_ID = '9040294929130520296'  # Sustituye con el ID de tu blog
API_KEY = 'AIzaSyCK6A27la3pe26zxSymiZ9gcZJk2ryz2MU'  # Sustituye con tu clave de API de Blogger
BLOGGER_API_URL = f'https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts?key={API_KEY}'

last_post_id = None  # Para almacenar el último ID de entrada procesado

def send_message(text, url):
    """
    Función para enviar un mensaje al grupo de Telegram con un botón de URL.
    """
    url_button = {
        'text': 'Ir al Reproductor',
        'url': url
    }
    message_data = {
        'chat_id': CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown',  # Usamos Markdown para dar formato al mensaje
        'reply_markup': {
            'inline_keyboard': [[url_button]]  # Añadir un botón con el enlace
        }
    }

    try:
        response = requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage', json=message_data)
        response.raise_for_status()  # Lanza una excepción si la solicitud falla
        message_id = response.json().get('result', {}).get('message_id')  # Obtener el ID del mensaje
        if message_id:
            pin_message(message_id)  # Fijar el mensaje recién enviado
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar el mensaje: {e}")

def pin_message(message_id):
    """
    Función para fijar el mensaje enviado en el grupo.
    """
    try:
        pin_url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/pinChatMessage'
        payload = {
            'chat_id': CHAT_ID,
            'message_id': message_id
        }
        response = requests.post(pin_url, data=payload)
        response.raise_for_status()  # Lanza una excepción si la solicitud falla
        print("Mensaje fijado correctamente.")
    except requests.exceptions.RequestException as e:
        print(f"Error al fijar el mensaje: {e}")

def send_bot_status():
    """
    Función para enviar un mensaje que indique que el bot está activado.
    """
    message = "🔔 **Bot Activado y Funcionando!** 🔔\n\nEstoy monitoreando SueFlix para compartir nuevo contenido. ¡Listo para recibir Peliculas Y Series! 🚀"
    send_message(message, None)
    print("Bot activado y funcionando!")

def clean_html(content):
    """
    Función para limpiar el HTML y extraer solo el texto plano de las etiquetas <p>.
    Utiliza BeautifulSoup para eliminar las etiquetas HTML.
    """
    soup = BeautifulSoup(content, 'html.parser')
    paragraphs = soup.find_all('p')  # Encuentra todas las etiquetas <p>
    text = ' '.join([p.get_text(separator=' ', strip=True) for p in paragraphs])  # Extrae el texto de cada párrafo
    return text

def check_new_posts():
    """
    Función para comprobar si hay nuevas publicaciones en el blog.
    """
    global last_post_id
    try:
        # Realizar la solicitud a la API de Blogger
        response = requests.get(BLOGGER_API_URL)
        response.raise_for_status()  # Lanza una excepción si la solicitud falla
        
        posts = response.json().get('items', [])
        
        if posts:
            latest_post = posts[0]
            if latest_post['id'] != last_post_id:
                last_post_id = latest_post['id']
                title = latest_post['title']
                # Limpiar el contenido HTML y obtener el resumen de los <p> tags
                summary = clean_html(latest_post.get('content', 'No summary available'))[:150]  # Obtener los primeros 150 caracteres del texto limpio
                url = latest_post['url']
                # Obtener las etiquetas (labels) de la publicación
                labels = ', '.join([f"#{label}" for label in latest_post.get('labels', ['Sin etiquetas'])])  # Añadir el signo '#' a las etiquetas
                
                # Crear el mensaje atractivo para enviar
                message = f"🔥 **¡Nueva Pelicula agregada!** 🔥\n\n" \
                          f"**🌟 Título:** {title} 🌟\n\n" \
                          f"**📝 Resumen:** {summary}...\n\n" \
                          f"**📑 Etiquetas:** {labels}\n\n" \
                          f"🎬 **LINK:** [IR AL REPRODUCTOR]({url})"

                send_message(message, url)  # Enviar el mensaje con el botón
    except requests.exceptions.RequestException as e:
        print(f"Error al verificar las publicaciones: {e}")

if __name__ == '__main__':
    send_bot_status()  # Envía el mensaje de "bot activado"
    
    while True:
        check_new_posts()
        time.sleep(60)  # Espera 60 segundos antes de volver a verificar
