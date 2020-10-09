import pandas as pd
import requests
import io
import streamlit as st
import plotly.graph_objects as go


@st.cache
def get_data(online=True):
    if online == True:
        url = "https://momo.isciii.es/public/momo/data"
        csvdoc = requests.get(url).content
        momo_raw = pd.read_csv(io.StringIO(csvdoc.decode('ISO-8859-1')), error_bad_lines=False)
    else:
        momo_raw = pd.read_csv("data.csv")

    momo_raw["nombre_ambito"] = momo_raw.apply(lambda x: str(x['nombre_ambito']).split(",")[0], axis=1)
    momo_raw["nombre_ambito"] = momo_raw["nombre_ambito"].replace("nan", ' España', regex=True)

    sex = momo_raw["nombre_sexo"].unique()
    age = momo_raw["nombre_gedad"].unique()
    regions = momo_raw["nombre_ambito"].unique()
    regions = sorted(regions)
    return momo_raw, sex, regions, age



def user_filters(sex, regions, age):
    st.sidebar.text("Selecciona los filtros a aplicar")
    selected_communities = st.sidebar.selectbox('Region', regions)
    selected_age = st.sidebar.selectbox('Grupos de Edad', age)
    selected_sex = st.sidebar.selectbox('Sexo', sex)

    days_to_delete = st.sidebar.slider('La información sobre los últimos días no es del todo fiable. '
                                       'Por lo que recomendamos no considerar los ultimos días.'
                                       '¿Cuantos días quieres quitar?', 1, 21, 14)

    mortality_rate = st.sidebar.slider('Mortalidad del Virus', min_value=0.0, max_value=20.0, value=1.0, step=0.1,
                                       format="%.2f%%")
    days_to_death = st.sidebar.slider('Días medios desde contagio hasta fallecimiento', min_value=7, max_value=30,
                                      value=18, step=1)

    return selected_communities, selected_age, selected_sex, days_to_delete, mortality_rate, days_to_death


def filtering_momo(momo, selected_sex, selected_age, selected_communities):
    momo1 = momo[momo["nombre_sexo"] == selected_sex]
    momo2 = momo1[momo1["nombre_gedad"] == selected_age]
    momo3 = momo2[momo2["nombre_ambito"] == selected_communities]
    momo3["fecha_defuncion"] = momo3["fecha_defuncion"].astype("datetime64")

    try:
        momo3.drop(columns=["ambito", "cod_ambito", "cod_ine_ambito", "nombre_ambito", "cod_sexo",
                                "nombre_sexo", "cod_gedad", "nombre_gedad", "defunciones_observadas_lim_sup",
                                "defunciones_observadas_lim_inf"], inplace=True)
        momo3.rename(columns={"defunciones_esperadas": "expected_deaths",
                                  "defunciones_observadas": "observed_deaths",
                                  "fecha_defuncion": "date"}, inplace=True)
    except:
        print("There was an error dropping and renaming columns")
        pass
    return momo3


def contagiuous(momo, days_to_death, mortality_rate, days_to_delete):
    momo = momo.iloc[:-days_to_delete, :]

    momo["Exceso de Defunciones"] = momo["observed_deaths"] - momo["expected_deaths"]

    momo['Exceso de Defunciones'].loc[(momo['Exceso de Defunciones'] < 0)] = 0

    momo["Contagiados"] = momo["Exceso de Defunciones"] / mortality_rate
    momo["Contagiados"] = momo["Contagiados"].shift(periods=-days_to_death, fill_value=None)

    start_date = '2020-02-01'
    end_date = max(momo["date"])

    momo = momo.set_index("date").resample('W-SUN').sum()  # .iloc[0:-1,]
    momo_relevant_dates = (momo.index > start_date) & (momo.index <= end_date)
    relevant_momo = momo.loc[momo_relevant_dates]

    return relevant_momo


def plot_timeline(momo, variable, selected_communities, selected_age, selected_sex):
    # Create traces
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=momo.index, y=momo[variable], mode='lines+markers', name='Calculated Deaths'))

    fig.update_layout(
        title=(variable + " en "+ str(selected_communities).strip() + ", Edad: " + str(selected_age) + ", Sexo: " + str(selected_sex)),
        xaxis_title="Semana",
        yaxis_title=variable,
        yaxis=dict(rangemode='tozero'),
        legend_orientation="h",
        font=dict(
            # family="Courier New, monospace",
            size=13,
            color="#7f7f7f"
        ))
    st.write(fig)


def main():
    st.title('Analizando el impacto del Covid-19 por Comunidad Autónoma')
    momo_raw, sex, regions, age = get_data(online=True)

    selected_communities, selected_age, selected_sex, days_to_delete, mortality_rate, days_to_death = user_filters(sex, regions, age)

    momo = filtering_momo(momo_raw, selected_sex, selected_age, selected_communities)

    momo = contagiuous(momo, days_to_death, mortality_rate, days_to_delete)


    st.write("En el siguiente gráfico se pueden observar "
             "las diferencias entre fallecimientos esperados y fallecimientos observados en "
             + str(selected_communities) + ". Asumimos que estas diferencias son provocadas por el Covid-19")

    plot_timeline(momo, variable="Exceso de Defunciones",
                  selected_communities=selected_communities, selected_age=selected_age, selected_sex=selected_sex)



    st.write("En el siguiente gráfico se pueden observar "
             "las diferencias entre fallecimientos esperados y fallecimientos observados en "
             + str(selected_communities) + ". Estas diferencias son atribuibles principalmente al Covid-19")

    plot_timeline(momo, variable="Contagiados",
                  selected_communities=selected_communities, selected_age=selected_age, selected_sex=selected_sex)


if __name__ == '__main__':
    main()
