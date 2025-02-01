from utils.transform import Transform
from utils.extract import Extract
from utils.load import Load
from datetime import datetime
import streamlit as st
import pandas as pd

def app():

    st.header('Formulario de nuevos clientes')

    # Cargar los datos
    data = Extract.load_data("Base_de_datos_clientes", "clientes")
    prices = Extract.load_data("Base_de_datos_clientes", "precios unitarios")

    # Extraer valores únicos de la columna 'nombre'
    df_unique = data['razón_social'].drop_duplicates()
    names_list = df_unique.unique()

    # Seleccionar la compañía fuera del formulario para que sea dinámico
    company_name = st.selectbox("Compañía:", tuple(names_list),index=False)

    # Filtrar los datos con base en el nombre de la compañía seleccionado
    if company_name:
        df_filtered = data[data['razón_social'] == company_name]
        try:
            df_price_filtered = prices[prices['razón_social'] == company_name]
            # df_max_p = df_price_filtered.loc[df_price_filtered['versión'].idxmax()]
            df_max_p = df_price_filtered.loc[ df_price_filtered.groupby('ruta')['versión'].idxmax()]

            # Reset the index for a clean result if needed
            df_max_p = df_max_p.reset_index(drop=True)

        except:
            df_price_filtered = pd.DataFrame()

        # Mostrar los detalles del cliente con la versión máxima
        df_max_v = df_filtered.loc[df_filtered['versión'].idxmax()]
        print(df_max_v)


        st.write(f"Has seleccionado la compañía: {df_max_v['razón_social']}")
        complete_general_information = False
        complete_price_information = False
        route_option = False
        date_added = False

        customer_id = str(df_max_v['cliente_id'])


        # Lista de campos modificables
        if df_price_filtered.empty:
            st.write("Este cliente no tiene información de precios. Selecciona *Nueva Ruta* si quieres introducirlos.")
            fields = [
                "Nombre persona contacto","CIF", "Email","Otros correos electrónicos", "Teléfono",
                "Teléfono persona contacto","Dirección",
                "Código Postal", "Municipio", "Provincia",
                "País", "Número de empleados", "Industria","Nueva Ruta"
            ]
        else:
            fields = [
                "Nombre persona contacto","CIF", "Email","Otros correos electrónicos", "Teléfono",
                "Teléfono persona contacto","Dirección",
                "Código Postal", "Municipio", "Provincia",
                "País", "Número de empleados", "Industria" ,
                "Precio por unidad de salida","Precio por kilómetro",
                "Precio unitario de trabajo de grúa",
                "Precio por unidad de descarga",
                "Precio por unidad de salida (servicio mínimo)","Precio por kilómetro (servicio mínimo)",
                "Precio unitario de trabajo de grúa (servicio mínimo)",
                "Precio por unidad de descarga (servicio mínimo)",
                "Nueva Ruta"
            ]

        email_warning = False

        # Crear multiselect para que el usuario elija los campos a modificar
        selected_fields = st.multiselect("Seleccione los campos que desea modificar:", fields)

        contact_name = df_max_v['nombre_contacto']
        if "Nombre persona contacto" in selected_fields:
            contact_name = st.text_input(f"Nombre persona contacto (Actual: {df_max_v['nombre_contacto']}):")
            contact_name = Transform.capital_letters(contact_name)
            complete_general_information = True

        cif = df_max_v['cif']
        if "CIF" in selected_fields:
            cif = st.text_input(f"CIF (Actual: {df_max_v['cif']}):")
            cif = Transform.capital_letters(cif)
            complete_general_information = True

        email = df_max_v['correo_electrónico']
        if "Email" in selected_fields:
            email = st.text_input(f"Email (Actual: {df_max_v['correo_electrónico']}):")
            email_warning = False
            # Validar en tiempo real el formato del correo electrónico
            if "@" not in email:
                email_warning = True
                st.warning("¡No es una dirección de correo electrónico válida!")
            if not email_warning and email:
                email = Transform.lowercase_letters(email)
                complete_general_information = True

        other_emails = df_max_v['otros_correos_electrónicos']
        if "Otros correos electrónicos" in selected_fields:
            other_emails = st.text_area(f"Otros correos electrónicos (Actual: {df_max_v['otros_correos_electrónicos']}):")
            other_emails = Transform.lowercase_letters(other_emails)
            complete_general_information = True

        phone = df_max_v['teléfono']
        if "Teléfono" in selected_fields:
            phone_input = st.number_input(f"Teléfono (Actual: {df_max_v['teléfono']}):",step=1, min_value=0,value=None)
            # Check for empty input before conversion
            phone = int(phone_input) if phone_input else df_max_v['teléfono']
            complete_general_information = True

        contact_phone = df_max_v['teléfono_contacto']
        if "Teléfono persona contacto" in selected_fields:
            phone_input = st.number_input(f"Teléfono persona contacto (Actual: {df_max_v['teléfono_contacto']}):",step=1, min_value=0)
            # Check for empty input before conversion
            contact_phone = int(phone_input) if phone_input else df_max_v['teléfono_contacto']
            complete_general_information = True

        address = df_max_v['domicilio']
        if "Dirección" in selected_fields:
            address = st.text_input(f"Dirección (Actual: {df_max_v['domicilio']}):")
            address = Transform.capital_letters(address)
            complete_general_information = True

        code = df_max_v['codigo_postal']
        if "Código Postal" in selected_fields:
            code_input = st.number_input(f"Código Postal (Actual: {df_max_v['codigo_postal']}):",step=1, min_value=0,value=None)
            # Check for empty input before conversion
            code = int(code_input) if code_input else int(df_max_v['codigo_postal'])
            complete_general_information = True

        municipality = df_max_v['municipio']
        if "Municipio" in selected_fields:
            municipality = st.text_input(f"Municipio (Actual: {df_max_v['municipio']}):")
            municipality = Transform.capital_letters(municipality)
            complete_general_information = True

        city = df_max_v['provincia']
        if "Provincia" in selected_fields:
            city = st.text_input(f"Provincia (Actual: {df_max_v['provincia']}):")
            city = Transform.capital_letters(city)
            complete_general_information = True

        country = df_max_v['país']
        if "País" in selected_fields:
            country = st.text_input(f"País (Actual: {df_max_v['país']}):")
            country = Transform.capital_letters(country)
            complete_general_information = True

        n_employees = df_max_v['n_empleados']
        if "Número de empleados" in selected_fields:
            n_employees_input = st.number_input(f"Número de empleados (Actual: {df_max_v['n_empleados']}):",step=1, min_value=0,value=None)
            # Check for empty input before conversion
            n_employees = int(n_employees_input) if n_employees_input else df_max_v['n_empleados']
            complete_general_information = True

        industry = df_max_v['industria']
        if "Industria" in selected_fields:
            industry = st.selectbox("Industria",
                                    ("AGRICULTURA, SILVICULTURA Y PESCA", "MINERÍA Y CANTERAS", "MANUFACTURAS",
                                        "SUMINISTRO DE ELECTRICIDAD, GAS, VAPOR Y AIRE ACONDICIONADO",
                                        "ABASTECIMIENTO DE AGUA; ALCANTARILLADO, GESTIÓN DE RESIDUOS Y ACTIVIDADES DE REMEDIACIÓN",
                                        "CONSTRUCCIÓN", "COMERCIO AL POR MAYOR Y AL POR MENOR; REPARACIÓN DE VEHÍCULOS DE MOTOR Y MOTOCICLETAS",
                                        "TRANSPORTE Y ALMACENAMIENTO", "ACTIVIDADES DE ALOJAMIENTO Y SERVICIO DE ALIMENTACIÓN",
                                        "INFORMACIÓN Y COMUNICACIÓN", "ACTIVIDADES FINANCIERAS Y DE SEGUROS",
                                        "ACTIVIDADES INMOBILIARIAS", "ACTIVIDADES PROFESIONALES, CIENTÍFICAS Y TÉCNICAS",
                                        "ACTIVIDADES DE SERVICIOS ADMINISTRATIVOS Y DE APOYO",
                                        "ADMINISTRACIÓN PÚBLICA Y DEFENSA; SEGURIDAD SOCIAL OBLIGATORIA",
                                        "EDUCACIÓN", "ACTIVIDADES DE SALUD HUMANA Y TRABAJO SOCIAL",
                                        "ARTES, ENTRETENIMIENTO Y RECREACIÓN", "OTRAS ACTIVIDADES DE SERVICIO",
                                        "ACTIVIDADES DE LOS HOGARES COMO EMPLEADORES; ACTIVIDADES DE PRODUCCIÓN DE BIENES Y SERVICIOS NO DIFERENCIADOS DE LOS HOGARES PARA USO PROPIO",
                                        "ACTIVIDADES DE ORGANIZACIONES Y ORGANISMOS EXTRATERRITORIALES"))
            complete_general_information = True

        if not df_price_filtered.empty:
            route = df_max_p['ruta'].tolist()

            if ("Precio por unidad de salida" in selected_fields or "Precio por kilómetro" in selected_fields or
                                 "Precio unitario de trabajo de grúa" in selected_fields or "Precio por unidad de descarga" in selected_fields  or "Precio por unidad de salida (servicio mínimo)" in selected_fields or "Precio por kilómetro (servicio mínimo)" in selected_fields or
                                 "Precio unitario de trabajo de grúa (servicio mínimo)" in selected_fields or "Precio por unidad de descarga (servicio mínimo)" in selected_fields):


                if int(len(route))> 1:
                    options = route + ["TODAS"]
                    route_option = st.radio("Para qué ruta(s) quieres modificar los precios?:",options=options)
                    if route_option != "TODAS":
                        print(route_option)

                        version_price = int((df_max_p["versión"][df_max_p["ruta"]==route_option]).iloc[0]) + 1

                        exit_price = float((df_max_p["precio_unidad_salida"][df_max_p["ruta"]==route_option]).iloc[0])
                        if "Precio por unidad de salida" in selected_fields:
                            exit_price_input = st.number_input(f"Precio unitario de salida (Actual para {route_option}: {float((df_max_p['precio_unidad_salida'][df_max_p['ruta']==route_option]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                            # Check for empty input before conversion
                            exit_price = float(exit_price_input) if exit_price_input else float((df_max_p["precio_unidad_salida"][df_max_p["ruta"]==route_option]).iloc[0])
                            complete_price_information = True

                        km_price = float((df_max_p["precio_kilómetro"][df_max_p["ruta"]==route_option]).iloc[0])
                        if "Precio por kilómetro" in selected_fields:
                            km_price_input = st.number_input(f"Precio por kilómetro (Actual para {route_option}: {float((df_max_p['precio_kilómetro'][df_max_p['ruta']==route_option]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                            # Check for empty input before conversion
                            km_price = float(km_price_input) if km_price_input else float((df_max_p["precio_kilómetro"][df_max_p["ruta"]==route_option]).iloc[0])
                            complete_price_information = True

                        crane_price = float((df_max_p["precio_trabajo_grúa"][df_max_p["ruta"]==route_option]).iloc[0])
                        if "Precio unitario de trabajo de grúa" in selected_fields:
                            crane_price_input = st.number_input(f"Precio unitario de trabajo de grúa (Actual para {route_option}: {float((df_max_p['precio_trabajo_grúa'][df_max_p['ruta']==route_option]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                            # Check for empty input before conversion
                            crane_price = float(crane_price_input) if crane_price_input else float((df_max_p["precio_trabajo_grúa"][df_max_p["ruta"]==route_option]).iloc[0])
                            complete_price_information = True

                        discharge_price = float((df_max_p["precio_descarga"][df_max_p["ruta"]==route_option]).iloc[0])
                        if "Precio por unidad de descarga" in selected_fields:
                            discharge_price_input = st.number_input(f"Precio por unidad de descarga (Actual para {route_option}: {float((df_max_p['precio_descarga'][df_max_p['ruta']==route_option]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                            # Check for empty input before conversion
                            discharge_price = float(discharge_price_input) if discharge_price_input else float((df_max_p["precio_descarga"][df_max_p["ruta"]==route_option]).iloc[0])
                            complete_price_information = True

                        exit_price_ms = float((df_max_p["precio_unidad_salida_sm"][df_max_p["ruta"]==route_option]).iloc[0])
                        if "Precio por unidad de salida (servicio mínimo)" in selected_fields:
                            exit_price_input = st.number_input(f"Precio unitario de salida - servicio mínimo (Actual para {route_option}: {float((df_max_p['precio_unidad_salida_sm'][df_max_p['ruta']==route_option]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                            # Check for empty input before conversion
                            exit_price = float(exit_price_input) if exit_price_input else float((df_max_p["precio_unidad_salida_sm"][df_max_p["ruta"]==route_option]).iloc[0])
                            complete_price_information = True

                        km_price_ms = float((df_max_p["precio_kilómetro_sm"][df_max_p["ruta"]==route_option]).iloc[0])
                        if "Precio por kilómetro (servicio mínimo)" in selected_fields:
                            km_price_input = st.number_input(f"Precio por kilómetro - servicio mínimo (Actual para {route_option}: {float((df_max_p['precio_kilómetro_sm'][df_max_p['ruta']==route_option]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                            # Check for empty input before conversion
                            km_price = float(km_price_input) if km_price_input else float((df_max_p["precio_kilómetro_sm"][df_max_p["ruta"]==route_option]).iloc[0])
                            complete_price_information = True

                        crane_price_ms = float((df_max_p["precio_trabajo_grúa_sm"][df_max_p["ruta"]==route_option]).iloc[0])
                        if "Precio unitario de trabajo de grúa (servicio mínimo)" in selected_fields:
                            crane_price_input = st.number_input(f"Precio unitario de trabajo de grúa - servicio mínimo (Actual para {route_option}: {float((df_max_p['precio_trabajo_grúa_sm'][df_max_p['ruta']==route_option]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                            # Check for empty input before conversion
                            crane_price = float(crane_price_input) if crane_price_input else float((df_max_p["precio_trabajo_grúa_sm"][df_max_p["ruta"]==route_option]).iloc[0])
                            complete_price_information = True

                        discharge_price_ms = float((df_max_p["precio_descarga_sm"][df_max_p["ruta"]==route_option]).iloc[0])
                        if "Precio por unidad de descarga (servicio mínimo)" in selected_fields:
                            discharge_price_input = st.number_input(f"Precio por unidad de descarga - servicio mínimo (Actual para {route_option}: {float((df_max_p['precio_descarga_sm'][df_max_p['ruta']==route_option]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                            # Check for empty input before conversion
                            discharge_price = float(discharge_price_input) if discharge_price_input else float((df_max_p["precio_descarga_sm"][df_max_p["ruta"]==route_option]).iloc[0])
                            complete_price_information = True

                        row_for_price = [customer_id, company_name,route_option, exit_price,km_price,crane_price,discharge_price,exit_price_ms,km_price_ms,crane_price_ms,discharge_price_ms, version_price]


                        print(row_for_price)

                    if route_option == "TODAS":

                        list_of_rows = []

                        for r in route:
                            print(r)
                            version_price = int((df_max_p["versión"][df_max_p["ruta"]==r]).iloc[0]) + 1
                            print(version_price)

                            exit_price = float((df_max_p["precio_unidad_salida"][df_max_p["ruta"]==r]).iloc[0])
                            if "Precio por unidad de salida" in selected_fields:
                                exit_price_input = st.number_input(f"Precio unitario de salida (Actual para {r}: {float((df_max_p['precio_unidad_salida'][df_max_p['ruta']==r]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                                # Check for empty input before conversion
                                exit_price = float(exit_price_input) if exit_price_input else float((df_max_p["precio_unidad_salida"][df_max_p["ruta"]==r]).iloc[0])
                                complete_price_information = True

                            km_price = float((df_max_p["precio_kilómetro"][df_max_p["ruta"]==r]).iloc[0])
                            if "Precio por kilómetro" in selected_fields:
                                km_price_input = st.number_input(f"Precio por kilómetro (Actual para {r}: {float((df_max_p['precio_kilómetro'][df_max_p['ruta']==r]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                                # Check for empty input before conversion
                                km_price = float(km_price_input) if km_price_input else float((df_max_p["precio_kilómetro"][df_max_p["ruta"]==r]).iloc[0])
                                complete_price_information = True

                            crane_price = float((df_max_p["precio_trabajo_grúa"][df_max_p["ruta"]==r]).iloc[0])
                            if "Precio unitario de trabajo de grúa" in selected_fields:
                                crane_price_input = st.number_input(f"Precio unitario de trabajo de grúa (Actual para {r}: {float((df_max_p['precio_trabajo_grúa'][df_max_p['ruta']==r]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                                # Check for empty input before conversion
                                crane_price = float(crane_price_input) if crane_price_input else float((df_max_p["precio_trabajo_grúa"][df_max_p["ruta"]==r]).iloc[0])
                                complete_price_information = True

                            discharge_price = float((df_max_p["precio_descarga"][df_max_p["ruta"]==r]).iloc[0])
                            if "Precio por unidad de descarga" in selected_fields:
                                discharge_price_input = st.number_input(f"Precio por unidad de descarga (Actual para {r} : {float((df_max_p['precio_descarga'][df_max_p['ruta']==r]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                                # Check for empty input before conversion
                                discharge_price = float(discharge_price_input) if discharge_price_input else float((df_max_p["precio_descarga"][df_max_p["ruta"]==r]).iloc[0])
                                complete_price_information = True

                            exit_price_ms = float((df_max_p["precio_unidad_salida_sm"][df_max_p["ruta"]==r]).iloc[0])
                            if "Precio por unidad de salida (servicio mínimo)" in selected_fields:
                                exit_price_input = st.number_input(f"Precio unitario de salida - servicio mínimo (Actual para {r}: {float((df_max_p['precio_unidad_salida_sm'][df_max_p['ruta']==r]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                                # Check for empty input before conversion
                                exit_price = float(exit_price_input) if exit_price_input else float((df_max_p["precio_unidad_salida_sm"][df_max_p["ruta"]==r]).iloc[0])
                                complete_price_information = True

                            km_price_ms = float((df_max_p["precio_kilómetro_sm"][df_max_p["ruta"]==r]).iloc[0])
                            if "Precio por kilómetro (servicio mínimo)" in selected_fields:
                                km_price_input = st.number_input(f"Precio por kilómetro - servicio mínimo (Actual para {r}: {float((df_max_p['precio_kilómetro_sm'][df_max_p['ruta']==r]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                                # Check for empty input before conversion
                                km_price = float(km_price_input) if km_price_input else float((df_max_p["precio_kilómetro_sm"][df_max_p["ruta"]==r]).iloc[0])
                                complete_price_information = True

                            crane_price_ms = float((df_max_p["precio_trabajo_grúa_sm"][df_max_p["ruta"]==r]).iloc[0])
                            if "Precio unitario de trabajo de grúa (servicio mínimo)" in selected_fields:
                                crane_price_input = st.number_input(f"Precio unitario de trabajo de grúa - servicio mínimo (Actual para {r}: {float((df_max_p['precio_trabajo_grúa_sm'][df_max_p['ruta']==r]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                                # Check for empty input before conversion
                                crane_price = float(crane_price_input) if crane_price_input else float((df_max_p["precio_trabajo_grúa_sm"][df_max_p["ruta"]==r]).iloc[0])
                                complete_price_information = True

                            discharge_price_ms = float((df_max_p["precio_descarga_sm"][df_max_p["ruta"]==r]).iloc[0])
                            if "Precio por unidad de descarga (servicio mínimo)" in selected_fields:
                                discharge_price_input = st.number_input(f"Precio por unidad de descarga - servicio mínimo (Actual para {r}: {float((df_max_p['precio_descarga_sm'][df_max_p['ruta']==r]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                                # Check for empty input before conversion
                                discharge_price = float(discharge_price_input) if discharge_price_input else float((df_max_p["precio_descarga_sm"][df_max_p["ruta"]==r]).iloc[0])
                                complete_price_information = True

                            row_for_price_r = [customer_id, company_name,r, exit_price,km_price,crane_price,discharge_price,exit_price_ms,km_price_ms,crane_price_ms,discharge_price_ms, version_price]
                            print(row_for_price_r)
                            list_of_rows.append(row_for_price_r)
                else:
                    st.write(f"Los precios se aplican a la ruta actual: {str(route[0])}. Si deseas añadir una ruta, debes seleccionar *Nueva Ruta*.")
                    st.write(f"Y añadir los correspondientes datos.")
                    # Convertir valores numéricos de pandas a tipos nativos de Python

                    version_price =  int((df_max_p["versión"][df_max_p["ruta"]==route].iloc[0])) + 1

                    exit_price =  float((df_max_p["precio_unidad_salida"][df_max_p["ruta"] == route]).iloc[0])
                    if "Precio por unidad de salida" in selected_fields:
                        exit_price_input = st.number_input(f"Precio unitario de salida (Actual para {str(route[0])}: {float((df_max_p['precio_unidad_salida'][df_max_p['ruta'] == route]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                        # Check for empty input before conversion
                        exit_price = float(exit_price_input) if exit_price_input else float((df_max_p['precio_unidad_salida'][df_max_p['ruta'] == route]).iloc[0])
                        complete_price_information = True

                    km_price = float((df_max_p["precio_kilómetro"][df_max_p["ruta"]==route]).iloc[0])
                    if "Precio por kilómetro" in selected_fields:
                        km_price_input = st.number_input(f"Precio por kilómetro (Actual para {str(route[0])}: {float((df_max_p['precio_kilómetro'][df_max_p['ruta']==route]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                        # Check for empty input before conversion
                        km_price = float(km_price_input) if km_price_input else float((df_max_p["precio_kilómetro"][df_max_p["ruta"]==route]).iloc[0])
                        complete_price_information = True

                    crane_price = float((df_max_p["precio_trabajo_grúa"][df_max_p["ruta"]==route]).iloc[0])
                    if "Precio unitario de trabajo de grúa" in selected_fields:
                        crane_price_input = st.number_input(f"Precio unitario de trabajo de grúa (Actual para {str(route[0])}: {float((df_max_p['precio_trabajo_grúa'][df_max_p['ruta']==route]).iloc[0])}):", min_value=0)
                        # Check for empty input before conversion
                        crane_price = float(crane_price_input) if crane_price_input else float((df_max_p["precio_trabajo_grúa"][df_max_p["ruta"]==route]).iloc[0])
                        complete_price_information = True

                    discharge_price = float((df_max_p["precio_descarga"][df_max_p["ruta"]==route]).iloc[0])
                    if "Precio por unidad de descarga" in selected_fields:
                        discharge_price_input = st.number_input(f"Precio por unidad de descarga (Actual para {str(route[0])}: {float((df_max_p['precio_descarga'][df_max_p['ruta']==route]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                        # Check for empty input before conversion
                        discharge_price = float(discharge_price_input) if discharge_price_input else float((df_max_p["precio_descarga"][df_max_p["ruta"]==route]).iloc[0])
                        complete_price_information = True

                    exit_price_ms = float((df_max_p["precio_unidad_salida_sm"][df_max_p["ruta"]==route]).iloc[0])
                    if "Precio por unidad de salida (servicio mínimo)" in selected_fields:
                        exit_price_input = st.number_input(f"Precio unitario de salida - servicio mínimo (Actual para {route}: {float((df_max_p['precio_unidad_salida_sm'][df_max_p['ruta']==route]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                        # Check for empty input before conversion
                        exit_price = float(exit_price_input) if exit_price_input else float((df_max_p["precio_unidad_salida_sm"][df_max_p["ruta"]==route]).iloc[0])
                        complete_price_information = True

                    km_price_ms = float((df_max_p["precio_kilómetro_sm"][df_max_p["ruta"]==route]).iloc[0])
                    if "Precio por kilómetro (servicio mínimo)" in selected_fields:
                        km_price_input = st.number_input(f"Precio por kilómetro - servicio mínimo (Actual para {route}: {float((df_max_p['precio_kilómetro_sm'][df_max_p['ruta']==route]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                        # Check for empty input before conversion
                        km_price = float(km_price_input) if km_price_input else float((df_max_p["precio_kilómetro_sm"][df_max_p["ruta"]==route]).iloc[0])
                        complete_price_information = True

                    crane_price_ms = float((df_max_p["precio_trabajo_grúa_sm"][df_max_p["ruta"]==route]).iloc[0])
                    if "Precio unitario de trabajo de grúa (servicio mínimo)" in selected_fields:
                        crane_price_input = st.number_input(f"Precio unitario de trabajo de grúa - servicio mínimo (Actual para {route}: {float((df_max_p['precio_trabajo_grúa_sm'][df_max_p['ruta']==route]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                        # Check for empty input before conversion
                        crane_price = float(crane_price_input) if crane_price_input else float((df_max_p["precio_trabajo_grúa_sm"][df_max_p["ruta"]==route]).iloc[0])
                        complete_price_information = True

                    discharge_price_ms = float((df_max_p["precio_descarga_sm"][df_max_p["ruta"]==route]).iloc[0])
                    if "Precio por unidad de descarga (servicio mínimo)" in selected_fields:
                        discharge_price_input = st.number_input(f"Precio por unidad de descarga - servicio mínimo (Actual para {route}: {float((df_max_p['precio_descarga_sm'][df_max_p['ruta']==route]).iloc[0])}):", min_value=0.0,step=0.01,value=None)
                        # Check for empty input before conversion
                        discharge_price = float(discharge_price_input) if discharge_price_input else float((df_max_p["precio_descarga_sm"][df_max_p["ruta"]==route]).iloc[0])
                        complete_price_information = True

                    row_for_price = [customer_id, company_name,route[0], exit_price,km_price,crane_price,discharge_price,exit_price_ms,km_price_ms,crane_price_ms,discharge_price_ms, version_price]
                    print(f'row_for_price:{row_for_price}')
            if "Nueva Ruta" in selected_fields:
                new_route = str(st.text_input(f"Ruta nueva para este cliente:"))
                route_input = Transform.capital_letters(str(new_route))
                exit_price = st.number_input(f"Precio unitario de salida para nueva ruta:", min_value=0.0,step=0.01,value=None)
                km_price = st.number_input(f"Precio por kilómetro para nueva ruta:", min_value=0.0,step=0.01,value=None)
                crane_price = st.number_input(f"Precio unitario de trabajo de grúa para nueva ruta:", min_value=0.0,step=0.01,value=None)
                discharge_price = st.number_input(f"Precio por unidad de descarga para nueva ruta:", min_value=0.0,step=0.01,value=None)
                exit_price_ms = st.number_input("Precio unitario de salida (servicio mínimo)", min_value=0.0,value=None,step=0.01)
                km_price_ms = st.number_input("Precio por kilómetro (servicio mínimo)",min_value=0.0,value=None,step=0.01)
                crane_price_ms = st.number_input("Precio unitario de trabajo de grúa (servicio mínimo)", min_value=0.0,value=None,step=0.01)
                discharge_price_ms = st.number_input("Precio unitario por descarga (servicio mínimo)", min_value=0.0,value=None,step=0.01)
                version_price = 1
                if "Nueva Ruta" in selected_fields and ("Precio por unidad de salida" in selected_fields or "Precio por kilómetro" in selected_fields or
                                    "Precio unitario de trabajo de grúa" in selected_fields or "Precio por unidad de descarga" in selected_fields or "Precio por unidad de salida (servicio mínimo)" in selected_fields or "Precio por kilómetro (servicio mínimo)" in selected_fields or
                                    "Precio unitario de trabajo de grúa (servicio mínimo)" in selected_fields or "Precio por unidad de descarga (servicio mínimo)" in selected_fields):
                    row_for_price_new = [customer_id, company_name,route_input, exit_price,km_price,crane_price,discharge_price,exit_price_ms,km_price_ms,crane_price_ms,discharge_price_ms, version_price]
                    print(f'row_for_price_new:{row_for_price_new}')
                    complete_price_information = True
                elif "Nueva Ruta" in selected_fields and ("Precio por unidad de salida" not in selected_fields and "Precio por kilómetro" not in selected_fields and
                                    "Precio unitario de trabajo de grúa" not in selected_fields and "Precio por unidad de descarga" not in selected_fields  and "Precio por unidad de salida (servicio mínimo)" not in selected_fields and "Precio por kilómetro (servicio mínimo)" not in selected_fields and
                                    "Precio unitario de trabajo de grúa (servicio mínimo)" not in selected_fields and "Precio por unidad de descarga (servicio mínimo)" not in selected_fields) :
                    row_for_price = [customer_id, company_name,route_input, exit_price,km_price,crane_price,discharge_price,exit_price_ms,km_price_ms,crane_price_ms,discharge_price_ms, version_price]
                    complete_price_information = True
                if complete_price_information == False:
                    st.warning("Rellena toda la información sobre precios")

        elif df_price_filtered.empty and "Nueva Ruta" in selected_fields:
            route = str(st.text_input(f"Ruta nueva para este cliente:"))
            route_input = Transform.capital_letters(str(route))
            exit_price = st.number_input(f"Precio unitario de salida para nueva ruta:", min_value=0.0,step=0.01,value=None)
            km_price = st.number_input(f"Precio por kilómetro para nueva ruta:", min_value=0.0,step=0.01,value=None)
            crane_price = st.number_input(f"Precio unitario de trabajo de grúa para nueva ruta:", min_value=0.0,step=0.01,value=None)
            discharge_price = st.number_input(f"Precio por unidad de descarga para nueva ruta:", min_value=0.0,step=0.01,value=None)
            exit_price_ms = st.number_input("Precio unitario de salida (servicio mínimo)", min_value=0.0,value=None,step=0.01)
            km_price_ms = st.number_input("Precio por kilómetro (servicio mínimo)",min_value=0.0,value=None,step=0.01)
            crane_price_ms = st.number_input("Precio unitario de trabajo de grúa (servicio mínimo)", min_value=0.0,value=None,step=0.01)
            discharge_price_ms = st.number_input("Precio unitario por descarga (servicio mínimo)", min_value=0.0,value=None,step=0.01)
            version_price = 1

            if route and exit_price and km_price and crane_price and discharge_price and exit_price_ms and km_price_ms and crane_price_ms and discharge_price_ms:
                row_for_price = [customer_id, company_name,route_input, exit_price,km_price,crane_price,discharge_price,exit_price_ms,km_price_ms,crane_price_ms,discharge_price_ms, version_price]
                complete_price_information = True
            else:
                complete_price_information = False
                st.warning("Rellena toda la información sobre precios")

        if (complete_general_information or complete_price_information) and not date_added:
            date = st.date_input("Fecha actual", format="DD/MM/YYYY")
            # Preparar datos para guardar
            date_str = date.strftime("%Y-%m-%d")
            ingestion_date = datetime.now()
            ingestion_date_str = ingestion_date.strftime("%Y-%m-%d %H:%M:%S")

        if complete_general_information:
            version = int(df_max_v['versión']) + 1
            info = st.text_area("Información Adicional")
            if info != "":
                info = Transform.capital_letters(info)
            else: info = ''

            row = [str(customer_id),str(company_name), str(contact_name),str(cif),str(email),str(other_emails),int(phone),int(contact_phone),
    str(address),int(code),str(municipality),str(city),str(country),int(n_employees),str(industry),str(date_str),str(info),int(version),str(ingestion_date_str)]
            print(row)

        if complete_price_information:
            try:
                for r in list_of_rows:
                    index_to_insert = -1
                    r.insert(index_to_insert, date_str)
                    r.append(ingestion_date_str)
                    print(f"r:{r}")
            except:
                pass
            try:
                index_to_insert = -1
                row_for_price.insert(index_to_insert, date_str)
                row_for_price.append(ingestion_date_str)
                print(f"row_for_price:{row_for_price}")
            except:
                pass
            try:
                index_to_insert = -1
                row_for_price_new.insert(index_to_insert, date_str)
                row_for_price_new.append(ingestion_date_str)
                print(f"row_for_price_new:{row_for_price_new}")
            except:
                pass

        # Crear formulario de Streamlit dentro del bloque condicional
        with st.form(key='company_form', clear_on_submit=True):
            # Botón de envío
            submit_button = st.form_submit_button(label='¡Listo!')

            # Acciones después de enviar el formulario
            if submit_button and not email_warning:
                if complete_general_information:
                    Load().append_row("Base_de_datos_clientes", "clientes", row)
                if complete_price_information:
                    try:
                        for r in list_of_rows:
                            Load().append_row("Base_de_datos_clientes", "precios unitarios", r)
                    except:
                        pass
                    try:
                        Load().append_row("Base_de_datos_clientes", "precios unitarios", row_for_price)
                    except:
                        pass
                    try:
                        Load().append_row("Base_de_datos_clientes", "precios unitarios", row_for_price_new)
                    except:
                        pass
                st.success("¡Guardado con éxito!")
