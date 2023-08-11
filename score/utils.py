import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd
import numpy as np

def get_graph():
    buffer=BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png=buffer.getvalue()
    graph=base64.b64encode(image_png)
    graph=graph.decode('utf-8')
    buffer.close()
    return graph

def get_plot(data):
    imgs=[]
    plt.switch_backend('AGG')
    plt.rcParams['font.size']=16
    df = pd.DataFrame(data, columns=['ID Estudiante', 'Curso', 'Inglés', 'Lectura crítica', 'Matemáticas', 'Ciencias naturales', 'Competencias ciudadanas'])
    columnas=['Inglés', 'Lectura crítica', 'Matemáticas', 'Ciencias naturales', 'Competencias ciudadanas']
    Cursos=df['Curso'].unique()
    for col in columnas:
        clasificacion = df.groupby('Curso')[col].value_counts()
        # Numbers of pairs of bars you want
        N = len(Cursos)

        # Data on X-axis
        # Specify the values of blue bars (height)
        blue_bar = []
        # Specify the values of orange bars (height)
        orange_bar = []
        for curso in Cursos:
            if 'Alto' in clasificacion[curso]:
                blue_bar.append(clasificacion[curso]['Alto'])
            else:
                blue_bar.append(0)
            if 'Bajo' in clasificacion[curso]:
                orange_bar.append(clasificacion[curso]['Bajo'])
            else:
                orange_bar.append(0)
        # Position of bars on x-axis
        ind = np.arange(N)

        # Figure size
        plt.figure(figsize=(12,12))

        # Width of a bar 
        width = 0.3       
        # Plotting
        plt.bar(ind, blue_bar , width, label='Tendencia a puntaje alto')
        for i, bar in enumerate(blue_bar):
            plt.text(ind[i], blue_bar[i]+0.05, blue_bar[i])
        plt.bar(ind + width, orange_bar, width, label='Tendencia a puntaje bajo')
        for i, bar in enumerate(orange_bar):
            plt.text(ind[i]+width, orange_bar[i]+0.1, orange_bar[i])
        plt.xlabel('Cursos')
        plt.ylabel('Cantidad de estudiantes con puntajes altos y bajos por curso')
        plt.title("Predicciones del puntaje de {} de los estudiantes por curso".format(col))

        # xticks()
        # First argument - A list of positions at which ticks should be placed
        # Second argument -  A list of labels to place at the given locations
        plt.xticks(ind + width / 2, Cursos)

        # Finding the best position for legends and putting it
        plt.legend(loc='best')
        graph= get_graph()
        imgs.append(graph)
    return imgs