from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage
from django.views.decorators.csrf import csrf_exempt
import joblib
import numpy as np
import csv
import io

# Create your views here


def PrediccionTemplateAPIView(request):
    print('entre antess')

    if request.method == 'POST':
    #if request.FILES.get('csv_file'):
        print('entré', request.POST)
        print('FILES', request.FILES)
        
        error_message = 'Todo bien'
        predictions_model1 = []
        predictions_model2 = []
        predictions_model3 = []
        predictions_model4 = []
        predictions_model5 = []
        ids = []  # Lista para almacenar los IDs

        csv_content_file = request.FILES.get('csv_content_file')
        if csv_content_file:
            print('si encontró')
            csv_file = csv_content_file
            # return render(request, "index.html", {
            #         'error_message': error_message,
            #         'page_obj': page_obj  # Pasar el objeto de página a la plantilla
            #     })
        else:
            csv_file = request.FILES['csv_file']
        
        
        print('csv ',csv_file)
        # Verificar si el archivo es un CSV
        if not csv_file.name.endswith('.csv'):
            error_message = 'Por favor, sube un archivo CSV.'
        else:
            # Procesar el contenido del CSV
            data = []
            try:
                # Leer el archivo en modo de texto usando io.TextIOWrapper
                text_file = io.TextIOWrapper(csv_file.file, encoding='utf-8')
                print('text_file ',text_file)
                reader = csv.reader(text_file)
                # Omitir la primera fila (cabecera)
                print('reader ',reader)
                
                next(reader)
                for row in reader:
                    # Convertir cada subitem del item en un np.array
                    row_as_array = np.array(row[1:], dtype=float)  # Omitir la primera columna
                    data.append(row_as_array)

                    # Agregar el ID a la lista de IDs
                    ids.append(int(row[0]))
                
                # Verificar si data tiene elementos y realizar la predicción
                if len(data) > 0:
                    # Recorrer data y aplicar reshape(1, -1) a cada item
                    data_reshaped = [item.reshape(1, -1) for item in data]
                    # Cargar el modelo de predicción
                    modelo_prediccion_1 = joblib.load('ingles_model.pkl')
                    modelo_prediccion_2 = joblib.load('l_critica_model.pkl')
                    modelo_prediccion_3 = joblib.load('matematicas_model.pkl')
                    modelo_prediccion_4 = joblib.load('naturales_model.pkl')
                    modelo_prediccion_5 = joblib.load('sociales_ciudadanas_model.pkl')

                    # Diccionario para traducir los valores numéricos a textos
                    traducciones = {1: 'Bajo', 2: 'Alto'}

                    # Realizar la predicción con los dos modelos para cada item en data_reshaped
                    predictions_model1 = [traducciones[int(modelo_prediccion_1.predict(item)[0])] for item in data_reshaped]
                    predictions_model2 = [traducciones[int(modelo_prediccion_2.predict(item)[0])] for item in data_reshaped]
                    predictions_model3 = [traducciones[int(modelo_prediccion_3.predict(item)[0])] for item in data_reshaped]
                    predictions_model4 = [traducciones[int(modelo_prediccion_4.predict(item)[0])] for item in data_reshaped]
                    predictions_model5 = [traducciones[int(modelo_prediccion_5.predict(item)[0])] for item in data_reshaped]

                    # Convertir el objeto zip en una lista
                    predictions_list = list(zip(ids, predictions_model1, predictions_model2, predictions_model3, predictions_model4, predictions_model5))

                    # Obtener el número de página a partir del parámetro 'page' en la URL
                    page_number = request.GET.get('page',1)
                    # Crear un paginador con 10 registros por página
                    paginator = Paginator(predictions_list, 10)

                    try:
                        # Obtener la página solicitada
                        page_obj = paginator.get_page(page_number)
                    except EmptyPage:
                        # Si la página está fuera de rango, redireccionar a la última página
                        page_obj = paginator.get_page(paginator.num_pages)
                    return render(request, "index.html", {
                        'error_message': error_message,
                        'page_obj': page_obj  # Pasar el objeto de página a la plantilla
                    })
            except csv.Error as e:
                error_message = f'Hubo un error al leer el archivo CSV: {str(e)}'


        return render(request, "index.html", {
            'error_message': error_message
        })

    
    return render(request, "index.html")
