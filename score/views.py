from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage
from django.views.decorators.csrf import csrf_exempt
from .utils import get_plot
import joblib
import numpy as np
import csv
import io
import pandas as pd
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
        cursos=[] #Lista para guardar los cursos
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
                columnas=joblib.load('columnsorder.pkl')
                df = pd.read_csv(csv_file)
                id=df[['Documento de identificación (sin puntos)', 'Curso']]
                df=df.drop(columns=[df.columns[0], 'Documento de identificación (sin puntos)', 'Curso'])
                #Se aplica la función get_dummies para separar las variables categóricas
                for col in df.columns:
                    datos = pd.get_dummies(df[col])
                    df = pd.concat([
                    df.drop(col, axis = 1),
                    datos], axis = 1)
                for col in columnas:
                    if col in df.columns:
                        pass
                    else:
                        df[col] = 0
                #Se reacomodan las columnas del dataframe 2019_1 para coincidir con las de 2022_2
                columnas2=list(df.columns)
                for i, col in enumerate(columnas):
                    if(col==columnas2[i]):
                        print(col)
                        pass
                else:
                    for j, col2 in enumerate(columnas2):
                        if(col2==col):
                            x, y=columnas2.index(columnas2[i]), columnas2.index(columnas2[j])
                            columnas2[y], columnas2[x]= columnas2[x], columnas2[y]
                            df=df[columnas2]
                df.insert(0,'Documento',id['Documento de identificación (sin puntos)'])
                df.insert(1,'Curso',id['Curso'])
                ids=df['Documento'].tolist()
                cursos=df['Curso'].tolist()
                #csv_file=df.to_csv(index=False)
                # Leer el archivo en modo de texto usando io.TextIOWrapper
                #text_file = io.StringIO(csv_file)
                #print('text_file ',text_file)
                #reader = csv.reader(csv_file)
                # Omitir la primera fila (cabecera)
                #print('reader ',reader)
                
                #next(reader)
                #Guardar las filas como arrays
                for i in range(len(df)):
                    # Convertir cada subitem del item en un np.array
                    row = df.iloc[i, 2:]
                    row_as_array = row.to_numpy() # Omitir la primera columna
                    data.append(row_as_array)
                    
                
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
                    predictions_list = list(zip(ids, cursos, predictions_model1, predictions_model2, predictions_model3, predictions_model4, predictions_model5))
                    graphs=get_plot(predictions_list)
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
                        'page_obj': page_obj,  # Pasar el objeto de página a la plantilla
                        'graphs':graphs
                    })
            except csv.Error as e:
                error_message = f'Hubo un error al leer el archivo CSV: {str(e)}'


        return render(request, "index.html", {
            'error_message': error_message
        })

    
    return render(request, "index.html")

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def export_csv(request):
    error_message = 'Todo bien'
    predictions_model1 = []
    predictions_model2 = []
    predictions_model3 = []
    predictions_model4 = []
    predictions_model5 = []
    ids = []  # Lista para almacenar los IDs
    cursos=[]
    if request.method == 'POST':
        print('entréeee')
        csv_content_file = request.FILES.get('csv_content_file')
        if csv_content_file:
            print('si encontró')
            csv_file = csv_content_file
        
        print('csv ',csv_file)
        # Verificar si el archivo es un CSV
        if not csv_file.name.endswith('.csv'):
            error_message = 'Por favor, sube un archivo CSV.'
        else:
            # Procesar el contenido del CSV
            data = []
            try:
                columnas=joblib.load('columnsorder.pkl')
                df = pd.read_csv(csv_file)
                id=df[['Documento de identificación (sin puntos)', 'Curso']]
                df=df.drop(columns=[df.columns[0], 'Documento de identificación (sin puntos)', 'Curso'])
                #Se aplica la función get_dummies para separar las variables categóricas
                for col in df.columns:
                    datos = pd.get_dummies(df[col])
                    df = pd.concat([
                    df.drop(col, axis = 1),
                    datos], axis = 1)
                for col in columnas:
                    if col in df.columns:
                        pass
                    else:
                        df[col] = 0
                #Se reacomodan las columnas del dataframe 2019_1 para coincidir con las de 2022_2
                columnas2=list(df.columns)
                for i, col in enumerate(columnas):
                    if(col==columnas2[i]):
                        print(col)
                        pass
                else:
                    for j, col2 in enumerate(columnas2):
                        if(col2==col):
                            x, y=columnas2.index(columnas2[i]), columnas2.index(columnas2[j])
                            columnas2[y], columnas2[x]= columnas2[x], columnas2[y]
                            df=df[columnas2]
                df.insert(0,'Documento',id['Documento de identificación (sin puntos)'])
                df.insert(1,'Curso',id['Curso'])
                ids=df['Documento'].tolist()
                cursos=df['Curso'].tolist()
                #csv_file=df.to_csv(index=False)
                # Leer el archivo en modo de texto usando io.TextIOWrapper
                #text_file = io.StringIO(csv_file)
                #print('text_file ',text_file)
                #reader = csv.reader(csv_file)
                # Omitir la primera fila (cabecera)
                #print('reader ',reader)
                
                #next(reader)
                #Guardar las filas como arrays
                for i in range(len(df)):
                    # Convertir cada subitem del item en un np.array
                    row = df.iloc[i, 2:]
                    row_as_array = row.to_numpy() # Omitir la primera columna
                    data.append(row_as_array)
                
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

                    # Combinar los datos en una lista que contenga el ID y las cinco predicciones
                    combined_data = list(zip(ids, cursos, predictions_model1, predictions_model2, predictions_model3, predictions_model4, predictions_model5))

                    # Generar el archivo CSV con las predicciones
                    response = HttpResponse(content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename="predictions.csv"'

                    # Escribir los datos en el archivo CSV
                    writer = csv.writer(response)
                    writer.writerow(['ID Estudiante', 'Curso', 'Ingles', 'Lectura critica', 'Matematicas', 'Ciencias naturales', 'Competencias ciudadanas'])
                    for row in combined_data:
                        writer.writerow(row)

                    return response
                
            except csv.Error as e:
                error_message = f'Hubo un error al leer el archivo CSV: {str(e)}'
                HttpResponse(error_message)
        
