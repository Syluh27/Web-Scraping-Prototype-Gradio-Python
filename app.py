import gradio as gr
from scraper import scrape_quotes
import pandas as pd
import csv
import tempfile
import shutil

# Función para filtrar citas
def filter_quotes(filter_type, filter_value):
    quotes = scrape_quotes()
    if not quotes:
        return "No se pudieron obtener las citas. Intenta nuevamente.", None

    # Normalizar datos
    filter_value = filter_value.lower().strip() if filter_value else None
    if filter_type == "Todos":
        filtered_quotes = quotes
    elif filter_type == "Autor" and filter_value:
        filtered_quotes = [q for q in quotes if q['author'].lower() == filter_value]
    elif filter_type == "Etiqueta" and filter_value:
        filtered_quotes = [
            q for q in quotes if filter_value in [tag.lower() for tag in q['tags']]
        ]
    else:
        return "Por favor, proporciona un valor válido para filtrar.", None

    if not filtered_quotes:
        return "No se encontraron citas con ese criterio.", None

    # Formatear las citas para mostrar en texto
    formatted_quotes = [
        f"\"{q['quote']}\" - {q['author']} (Tags: {', '.join(q['tags'])})"
        for q in filtered_quotes
    ]

    # Convertir los datos filtrados a un DataFrame
    df = pd.DataFrame(filtered_quotes)
    return "\n\n".join(formatted_quotes), df

# Función para exportar a CSV
def handle_csv_export(filtered_quotes):
    # Verificar si el DataFrame está vacío
    if filtered_quotes is None or filtered_quotes.empty:
        return None

    # Convertir el DataFrame a una lista de diccionarios
    quotes = filtered_quotes.to_dict(orient="records")

    # Crear el archivo CSV en memoria
    csv_data = "quote, author, tags\n"
    for quote in quotes:
        tags = ', '.join(quote['tags'])  # Convertir la lista de tags en una cadena separada por comas
        csv_data += f'"{quote["quote"]}", "{quote["author"]}", "{tags}"\n'

    # Crear un archivo temporal
    tmp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', newline='', suffix='.csv')
    tmp_file.write(csv_data)
    tmp_file.close()

    # Renombrar el archivo temporal y retornar su nombre
    new_filename = "dataScraping.csv"
    shutil.move(tmp_file.name, new_filename)
    return new_filename

# Obtener valores únicos de autores y etiquetas para ayudar al usuario
def get_options():
    quotes = scrape_quotes()
    if not quotes:
        return "No se pudieron obtener datos."
    authors = sorted({q['author'] for q in quotes})
    tags = sorted({tag for q in quotes for tag in q['tags']})
    return f"Autores disponibles: {', '.join(authors)}\nEtiquetas disponibles: {', '.join(tags)}"

# Configurar la interfaz de Gradio
with gr.Blocks() as interface:
    gr.Markdown("# Quotes Scraper")
    gr.Markdown(
        "Obtén citas, autores y etiquetas del sitio 'Quotes to Scrape'. "
        "Elige si deseas ver todas las citas o filtrarlas por autor o etiqueta."
    )
    filter_type = gr.Radio(["Todos", "Autor", "Etiqueta"], label="Filtrar por")
    filter_value = gr.Textbox(label="Escribe el nombre del autor o etiqueta (opcional)")
    output_text = gr.Textbox(label="Citas obtenidas")
    output_table = gr.Dataframe(label="Citas en formato tabular", interactive=False)

    filter_button = gr.Button("Filtrar")
    filter_button.click(
        fn=filter_quotes,
        inputs=[filter_type, filter_value],
        outputs=[output_text, output_table]
    )

    gr.Markdown("### Opciones disponibles")
    options_output = gr.Textbox(label="Autores y etiquetas disponibles", interactive=False)
    options_button = gr.Button("Ver opciones disponibles")
    options_button.click(fn=get_options, inputs=[], outputs=options_output)

    # Botón para exportar a CSV
    export_button = gr.Button("Exportar a CSV")
    csv_output = gr.File(label="Descargar archivo CSV")
    export_button.click(fn=handle_csv_export, inputs=output_table, outputs=csv_output)

if __name__ == "__main__":
    interface.launch()
