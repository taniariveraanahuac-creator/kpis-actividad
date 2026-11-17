# 🚦 KPIs en acción · Liderazgo y Administración

Actividad por equipos: cada equipo elige un caso, descarga su macro de Excel, lee el semáforo de sus KPIs y presenta una decisión en 3 minutos.

**Página:** GitHub Pages · **Registro de equipos:** Google Sheets + Apps Script

---

## 📦 Qué hay en este repositorio

| Archivo | Para qué sirve |
|---|---|
| `index.html` | La página (estructura) |
| `styles.css` | Colores, tipografía, tema claro/oscuro e impresión |
| `app.js` | Casos, equipos, horario, tutorial, ejemplo y rúbrica |
| `config.js` | ⚙️ **Lo único que editas**: la URL de tu Apps Script |
| `macros/` | Las 10 macros de Excel (5 de Liderazgo, 5 de Administración) |
| `apps-script/Code.gs` | El "cerebro" que guarda los equipos en tu hoja de Google |
| `data/kpis.js` | Datos del tablero docente (se generan solos desde las macros) |
| `dashboard/` | Versión del tablero en **Streamlit** (Python), al estilo de *streamlit-sales-dashboard* |
| `scripts/build_data.py` + `.github/workflows/` | 🤖 Automatización: si cambias una macro, el tablero se actualiza solo |

> 🔒 **Las claves y los nombres de los estudiantes NO están en este repositorio.** Viven solo en tu hoja de Google privada. Nunca subas a GitHub el archivo `Base_KPIs_en_accion_PRIVADA.xlsx`.

---

## 🛠️ Puesta en marcha (una sola vez, ~15 minutos)

### Paso 1 · Crea la hoja de Google 🟩
1. Sube `Base_KPIs_en_accion_PRIVADA.xlsx` a tu Google Drive.
2. Ábrelo y elige **Archivo › Guardar como Hojas de cálculo de Google**. Trabaja siempre en esa copia.
3. Revisa que tenga 3 pestañas: **Claves**, **Equipos** y **Config**.

### Paso 2 · Pega el código del servidor 🧠
1. En la hoja: **Extensiones › Apps Script**.
2. Borra lo que aparezca y pega el contenido de `apps-script/Code.gs`.
3. Guarda (💾).

### Paso 3 · Publícalo como aplicación web 🌐
1. **Implementar › Nueva implementación** › tipo **Aplicación web**.
2. *Ejecutar como:* **Yo**. *Quién tiene acceso:* **Cualquier usuario**.
3. Pulsa **Implementar**, autoriza los permisos y **copia la URL** (termina en `/exec`).

> 💡 Comprueba que funciona: al abrir la URL en el navegador debes ver `"El servicio está activo."`

### Paso 4 · Conecta la página ✏️
Abre `config.js` y pega la URL entre las comillas:

```js
API_URL: 'https://script.google.com/macros/s/XXXXXXXX/exec',
```

### Paso 5 · Publica la página 🚀
1. **Settings › Pages** › *Branch:* `main` / *root* › **Save**.
2. En 1–2 minutos la página estará en `https://taniariveraanahuac-creator.github.io/kpis-actividad/`.

> ⚠️ Si subes archivos con **Add file › Upload files**, respeta las carpetas: las macros van dentro de `macros/`. Si quedan sueltas, la descarga falla.

---

## 👩‍🏫 Uso en clase

| Quién | Cómo entra | Qué puede hacer |
|---|---|---|
| 🎓 Estudiante | **Su matrícula + su correo institucional** (ej. `00633240` y `nombre@anahuac.mx`). Ya no hay que repartir claves | Ver solo su grupo, unirse a un equipo con un rol, salir, descargar su macro |
| 🧑‍🏫 Docente | Clave `DOC-XXXXXXXX` | Ver los dos grupos, asignar o mover estudiantes, fijar el horario y descargar el CSV |

- ⏰ **Horario:** el docente fija la apertura y el cierre en *Calendario y horario*. Fuera de ese horario los estudiantes no pueden inscribirse ni descargar.
- 🔄 La lista de equipos se actualiza sola cada 15 segundos (se cambia en `config.js`).
- 📊 Todo queda registrado en la pestaña **Equipos** de tu hoja de Google.

---

## 📊 Tablero de KPIs (solo docente)

Al entrar con la clave `DOC-` aparece **Tablero** en el menú. Sigue el patrón del proyecto *streamlit-sales-dashboard*:

**Excel → filtros → tarjetas de KPIs → gráficas.**

- 🎛️ **Filtros:** grupo, semáforo y mes (1 a 6).
- 🔢 **Tarjetas:** KPIs evaluados, cuántos en verde, cuántos en rojo y equipos con algún rojo.
- 📈 **Gráficas:** semáforo por caso, real ÷ meta × 100 y evolución de 6 meses.
- 🔑 Funciona como **clave de respuestas** al revisar las exposiciones. Los estudiantes no lo ven.

### Versión Streamlit (opcional)
```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```
Para publicarla gratis: [share.streamlit.io](https://share.streamlit.io) › **New app** › repositorio `kpis-actividad`, archivo `dashboard/app.py`.

## 🤖 Automatización

| Qué pasa | Quién lo hace |
|---|---|
| Cambias o reemplazas una macro en `macros/` | Tú |
| Se recalculan `data/kpis.js` y `dashboard/kpis_casos.xlsx` | GitHub Actions, solo |
| La página y el tablero muestran los datos nuevos | GitHub Pages, solo |

Puedes verlo en la pestaña **Actions** del repositorio. Si cambias un caso, su nombre o su archivo, edita la lista `CASES` en `scripts/build_data.py` y en `app.js`.

## 🔁 Cambios frecuentes

| Quiero… | Haz esto |
|---|---|
| Agregar un estudiante | Agrega una fila en **Claves** (`ID` como `L:16` o `A:22`, `Nombre`, `Matrícula`, `Correo`) y ejecuta `limpiarCache` en Apps Script |
| Cambiar el código de `Code.gs` | **Implementar › Gestionar implementaciones › ✏️ › Versión nueva**. La URL no cambia |
| Reiniciar la actividad | Borra las filas de **Equipos** (deja el encabezado) |
| Usarla con otro grupo | Reemplaza las filas de **Claves** con claves y nombres nuevos |

---

## ✨ Qué cambió respecto a la versión anterior

- ✅ Funciona fuera de Claude: GitHub Pages + Google Sheets, sin depender de permisos de "Contribuidor".
- 🔒 Las reglas se revisan en el servidor: la clave, un equipo por persona, máximo 5, roles sin repetir y el horario.
- 🙈 Los nombres de los estudiantes ya no viajan en el código público: solo los recibe quien entra con una clave válida.
- ⚡ La página pasó de 364 KB a unos 60 KB; las macros se descargan aparte.
- 🟢 Indicador "Equipos al día / Sin conexión" y reconexión automática.
- 🖨️ Rúbrica con botones **Limpiar** e **Imprimir o guardar en PDF**.
- 🔤 Se carga la tipografía de títulos que antes faltaba (Space Grotesk).
- ➖ Se quitó la "pista con IA", que solo funcionaba dentro de Claude.
- 📊 Nuevo tablero docente con filtros, tarjetas y gráficas, más versión en Streamlit.
- 🤖 GitHub Actions regenera los datos del tablero cuando cambian las macros.

---

*Los datos de los casos son ficticios y sirven solo para la actividad.*
