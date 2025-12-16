# 🤖 Discord Bot "Nekotina Remake"

Un bot de Discord moderno y multifuncional escrito en Python usando `discord.py`. Incluye sistemas de música, economía, niveles, moderación y un dashboard de configuración interactivo.

## ✨ Características Principales

- **🎵 Música**: Reproducción de alta calidad desde YouTube/Spotify (requiere FFmpeg).
- **💰 Economía**: Sistema de monedas, trabajos, apuestas (`gamble`, `roulette`, `slots`) y tienda.
- **📈 Niveles (XP)**: Sistema de experiencia por mensajes con notificaciones de nivel.
- **💍 Perfil y Matrimonios**: Perfiles personalizables con biografía y sistema de matrimonios dinámico.
- **⚙️ Dashboard**: Panel de configuración interactivo dentro de Discord para personalizar bienvenidas.
- **🛡️ Moderación**: Comandos de kick, ban, mute y sistema de advertencias.
- **👋 Bienvenidas**: Mensajes de bienvenida personalizables con imágenes/GIFs configurables.

## 🚀 Instalación y Uso

### prerrequisitos
- Python 3.9 o superior
- FFmpeg (para música)
- Un bot creado en el [Discord Developer Portal](https://discord.com/developers/applications)

### Pasos
1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/tu-repo.git
   cd tu-repo
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuración**
   Crea un archivo `config.json` en la carpeta raíz (o renombra uno de ejemplo) con el siguiente contenido:
   ```json
   {
       "TOKEN": "TU_TOKEN_DE_DISCORD_AQUI",
       "PREFIX": "&"
   }
   ```
   *Nota: El archivo `data/welcome_config.json` se creará automáticamente al configurar el dashboard.*

4. **Iniciar el bot**
   ```bash
   python main.py
   ```

## 🎮 Comandos Principales

El bot usa "Slash Commands" (/) y prefijo (`&`).

### 🛠️ Utilidad y Configuración
- `&sync`: Sincroniza los comandos slash (Usa `&sync .` para sincronizar instantáneamente en el servidor actual).
- `&dashboard`: Abre el panel interactivo para configurar el canal y mensaje de bienvenida.
- `&testwelcome`: Prueba la configuración de bienvenida actual.

### 👤 Perfil y Social
- `/profile`: Muestra tu tarjeta de perfil con Nivel, XP, Dinero y Pareja.
- `/marry <usuario>`: Propón matrimonio a alguien.
- `/divorce`: Divórciate de tu pareja actual.
- `/bio <texto>`: Configura tu biografía personal.

### 🎵 Música
- `/play <canción>`: Reproduce música.
- `/stop`, `/pause`, `/resume`, `/skip`: Controles de reproducción.

### 💰 Economía
- `/work`: Trabaja para ganar monedas.
- `/daily`: Reclama tu recompensa diaria.
- `/gamble <monto>`: Apuesta tus monedas.
- `/top coins`: Ver tabla de clasificación de dinero.

### 🎲 Diversión
- `/trivia`: Contesta preguntas de cultura general.
- `/meme`: Muestra un meme aleatorio.
- `/eightball`: Pregunta a la bola mágica.

## 📂 Estructura del Proyecto
- `main.py`: Punto de entrada del bot.
- `cogs/`: Módulos del bot (Música, Economía, etc.).
- `utils/`: Utilidades de interfaz (Embeds, UI Views).
- `data/`: Archivos JSON para persistencia de datos (Dinero, XP, Config).

## 📝 Notas
- Asegúrate de tener **FFmpeg** instalado y agregado al PATH del sistema para que funcione la música.
- La primera vez que inicies, ejecuta `&sync .` para ver los comandos slash inmediatamente.
