from getting_data import *


st.title('Analizando el impacto del Covid-19 por Comunidad Autónoma')
momo_raw, sex, regions, age = get_data(online=False)

selected_communities, selected_age, selected_sex, days_to_delete, mortality_rate, days_to_death = user_filters(sex, regions, age)

momo = filtering_momo(momo_raw, selected_sex, selected_age, selected_communities)

momo = contagiuous(momo, days_to_death, mortality_rate, days_to_delete)


st.write("En el siguiente gráfico se pueden observar "
         "las diferencias entre fallecimientos esperados y fallecimientos observados en "
         + str(selected_communities) + ". Estas diferencias son atribuibles principalmente al Covid-19")

plot_timeline(momo, variable="Exceso de Defunciones",
              selected_communities=selected_communities, selected_age=selected_age, selected_sex=selected_sex)



st.write("En el siguiente gráfico se pueden observar "
         "las diferencias entre fallecimientos esperados y fallecimientos observados en "
         + str(selected_communities) + ". Estas diferencias son atribuibles principalmente al Covid-19")

plot_timeline(momo, variable="Contagiados",
              selected_communities=selected_communities, selected_age=selected_age, selected_sex=selected_sex)

