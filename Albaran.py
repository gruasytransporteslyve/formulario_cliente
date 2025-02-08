from utils.transform import Transform
from utils.extract import Extract
from utils.load import Load
from datetime import datetime
from uuid import uuid4
import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
import os



def app():
    st.header('Formulario de nuevos clientes')

    # Cargar los datos
    data = Extract.load_data("Base_de_datos_clientes", "clientes")
    albaran = Extract.load_data("Base_de_datos_clientes", "albarán")
    prices = Extract.load_data("Base_de_datos_clientes", "precios unitarios")
    data_button = st.button("Volver a cargar datos")
    if data_button:
        st.cache_data.clear()  # Clear the cache
        st.write("Refresca la página")

    if not data.empty:
    # Extraer valores únicos de la columna 'nombre'
        df_unique = data['razón_social'].drop_duplicates()
        names_list = df_unique.unique()
    else:
        names_list=[]
    complete_information = False
    complete_information_price = False
    estimation = None

    opciones = ["Cliente Nuevo", "Cliente Habitual"]

    # Select fields to modify
    selected_fields = st.selectbox("Selecciona el tipo de empresa para crear el albarán:", opciones,index=None)

    if selected_fields == "Cliente Habitual":
        # Select company name outside of the form
        company_name = st.selectbox("Compañía:", tuple(names_list), index=None)

        if company_name:
            # Filter data based on selected company name
            df_filtered = data[data['razón_social'] == company_name]


            if not df_filtered.empty:  # Check if df_filtered is not empty
                df_max_v = df_filtered.loc[df_filtered['versión'].idxmax()]
                cliente_id = df_filtered['cliente_id'].unique()[0]
                print(cliente_id)

                # Display selected company details
                st.write(f"Has seleccionado la compañía: {df_max_v['razón_social']}")
                try:

                    # Now calculate the max and ensure it's not NaN
                    albaran_id = Load.generate_albaran_id(albaran)
                except ValueError as e:
                    # Handle the case where the conversion fails entirely
                    print("Error creating albarán_id")

                try:
                    df_price_filtered = prices[prices['razón_social'] == company_name]
                    # df_max_p = df_price_filtered.loc[df_price_filtered['versión'].idxmax()]
                    df_max_p = df_price_filtered.loc[ df_price_filtered['versión'].idxmax()]



                except:
                    print("df_price_filtered failed")
                    df_price_filtered = pd.DataFrame()


                st.write("""El DNI y la firma previstos a continuación se utilizarán únicamente para la creación del albarán.
                             En ningún caso se almacenarán individualmente, ni se utilizarán para otros fines distintos al anteriormente descrito.
                             La información prevista sobre la empresa, serán utilizados únicamente para mejorar nuestros servicios.""")
                consent = st.checkbox("Acepto")

                # Dynamically handle the number of tasks
                date = st.date_input("Fecha actual", value=datetime.now())

                truck = st.selectbox(f'Indica el camión que se ha necesitado:', ("Camión 1", "Camión 2", "Camión 3", "Camión 4"), key=f'truck', index=None)
                driver = st.selectbox(f'Indica el chófer para este trabajo:', ("Chófer 1", "Chófer 2", "Chófer 3"), key='driver', index=None)
                route = st.text_input(f'Indica la ruta para este trabajo:')
                route = Transform.capital_letters(route)
                exit_units = st.number_input(f'¿Cuántas unidades de salida?',step=1, min_value=0)
                km_units = st.number_input(f'¿Cuántos kilómetros?',step=0.01, min_value=0.0)
                crane = st.number_input(f'¿Cuántas unidades de trabajo de grúa?',step=1, min_value=0)
                discharge_units = st.number_input(f'¿Cuántas unidades de descarga?',step=1, min_value=0)
                minimum_service = st.checkbox("Servicio Mínimo")
                description = st.text_area('Descripción Trabajos realizados:')
                obs = st.text_area(f'Observaciones')
                email = df_max_v['correo_electrónico']
                date_str = date.strftime("%Y-%m-%d")
                ingestion_date = datetime.now()
                ingestion_date_str = ingestion_date.strftime("%Y-%m-%d %H:%M:%S")

                if driver and truck:
                    row = [str(albaran_id), df_max_v['cliente_id'], company_name, email, route, description,obs,exit_units,km_units, crane, discharge_units, minimum_service, truck, driver, date_str, consent,ingestion_date_str]
                    complete_information = True

                if not driver:
                    st.warning("Selecciona el conductor que ha realizado la tarea.")
                    complete_information = False
                if not truck:
                    st.warning("Selecciona el camión que se ha utilizado en la tarea.")
                    complete_information = False


                if consent:
                    dni = st.text_input("Escribe tu DNI:")
                # Create a canvas component
                canvas_result = st_canvas(
                    fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
                    stroke_width=3,#stroke_width,
                    stroke_color='#000',#stroke_color,
                    background_color='White',#bg_color,
                    update_streamlit=True,
                    height=150,
                    drawing_mode="freedraw",
                    point_display_radius= 0,
                    key="app",
                )


                if not df_price_filtered.empty and not minimum_service:
                    price_exit_units = float(df_max_p.loc['precio_unidad_salida'])
                    price_km_units = float(df_max_p.loc['precio_kilómetro'])
                    price_crane = float(df_max_p.loc['precio_trabajo_grúa'])
                    price_discharge_units = float(df_max_p.loc['precio_descarga'])
                    price_minimum_service = float(df_max_p.loc['precio_servicio_mínimo'])

                    total_price = price_exit_units * exit_units + price_km_units * km_units + price_crane * crane + price_discharge_units * discharge_units
                elif not df_price_filtered.empty and minimum_service:
                    total_price =  price_minimum_service

                st.write(f"Precio estimado:{round(float(total_price),2)}€")
                estimation = st.radio("¿Estás de acuerdo con este presupuesto?", options=["Sí", "No"])
                if estimation == "No":
                        estimation = st.number_input("Añade el valor que consideres más acertado", min_value=0.0,step=0.01,value=None)
                else:
                    estimation = round(total_price,2)

                if complete_information:
                        row.append(estimation)
            else:
                option = st.radio("Este cliente no tiene rango de precios registrado. ¿Quieres añadir un importe estimado de este albarán o añadir todos los precios?", options=["Añadir Manualmente", "Añadir todos los precios"])
                if option =="Añadir Manualmente":
                    estimation = st.number_input("Añade el importe de este albarán que consideres más acertado", min_value=0.0,step=0.01,value=None)
                    if complete_information:
                        row.append(estimation)
                        complete_information_price = True
                else :
                    exit_price = st.number_input(f"Precio unitario de salida:", min_value=0.0,step=0.01,value=None)
                    km_price = st.number_input(f"Precio por kilómetro:", min_value=0.0,step=0.01,value=None)
                    crane_price = st.number_input(f"Precio unitario de trabajo de grúa:", min_value=0.0,step=0.01,value=None)
                    discharge_price = st.number_input(f"Precio unitario por descarga:", min_value=0.0,step=0.01,value=None)
                    minimum_service_price = st.number_input(f"Precio por servicion mínimo:", min_value=0.0,step=0.01,value=None)

                    customer_id = str(uuid4())
                    version = 1

                    if exit_price and km_price and crane_price and discharge_price and minimum_service_price:
                        complete_information_price = True
                        row_price = [customer_id, transformed_name, exit_price,km_price,crane_price,discharge_price,minimum_service_price, date_str,version]
                        if minimum_service:
                            total_price = minimum_service_price
                        elif not minimum_service:
                            total_price = exit_price * exit_units + km_price * km_units + crane_price * crane + discharge_price * discharge_units
                        st.write(f"Precio estimado:{round(float(total_price),2)}€")
                        estimation = st.radio("¿Estás de acuerdo con este presupuesto?", options=["Sí", "No"])
                        if estimation == "No":
                            estimation = st.number_input("Añade el valor que consideres más acertado", min_value=0.0,step=0.01)
                        else:
                            estimation = round(total_price,2)
                    else:
                        complete_information_price = False
                        st.warning("Rellena toda la información sobre precios")
                    if complete_information_price and complete_information:
                        row.append(estimation)

                # Form for submission
                with st.form(key='company_form', clear_on_submit=True):
                    submit_button = st.form_submit_button(label='¡Listo!')

                    if submit_button and consent and canvas_result.image_data is not None and complete_information:
                        Load().append_row("Base_de_datos_clientes", "albarán", row)
                        if complete_information_price:
                            Load().append_row("Base_de_datos_clientes", "precios unitarios", row_price)

                        customer_details ={
                            "[Date]":str(date_str),
                            "[albarán_id]": str(albaran_id),
                            "[Company]":str(company_name),
                            "[Address]":str(df_max_v['domicilio']),
                            "[City]":str(df_max_v['provincia']),
                            "[Code]":str(df_max_v['codigo_postal']),
                            "[Cif]":str(df_max_v['cif'])
                        }
                        folder_id = st.secrets["folder_id"]

                        document_id = Load.upload_to_drive('template.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ,folder_id,str(company_name))
                        Transform.rename_file_in_drive(document_id,albaran_id,date_str)
                        new_document_id = Transform.convert_to_google_docs(document_id, True)
                        Load.replace_placeholders_in_doc(new_document_id,customer_details)

                        result_dict = {
                                "[Route]":str(route),
                                "[Work done]": str(description),
                                "[Obs]":str(obs),
                                "[Exit]":str(exit_units),
                                "[Km]":str(km_units),
                                "[Crane]":str(crane),
                                "[Discharge]":str(discharge_units)
                                }

                        result_dict["[dni]"] = str(dni)
                        result_dict["[price]"] = str(estimation)
                        print(result_dict)
                        Load.replace_placeholders_in_doc(new_document_id,result_dict)
                        image_id, image_link= Load.upload_image_to_google_drive(canvas_result)
                        Load.insert_image_in_document(new_document_id, image_link)
                        Extract.delete_file_from_image_url(image_link)
                        Transform.convert_doc_to_pdf_and_save(new_document_id,f"{albaran_id}_{date_str}")
                        # Extract.delete_file_from_google_drive(new_document_id)

                        st.success("¡Guardado con éxito!")

                    elif submit_button and consent==False and complete_information:
                        Load().append_row("Base_de_datos_clientes", "albarán", row)
                        if complete_information_price:
                            Load().append_row("Base_de_datos_clientes", "precios unitarios", row_price)
                        customer_details ={
                            "[Date]":str(date_str),
                            "[albarán_id]": str(albaran_id),
                            "[Company]":str(company_name),
                            "[Address]":str(df_max_v['domicilio']),
                            "[City]":str(df_max_v['provincia']),
                            "[Code]":str(df_max_v['codigo_postal']),
                            "[Cif]":str(df_max_v['cif'])
                        }
                        folder_id = st.secrets["folder_id"]

                        document_id = Load.upload_to_drive('template.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ,folder_id,str(company_name))
                        Transform.rename_file_in_drive(document_id,albaran_id,date_str)
                        new_document_id = Transform.convert_to_google_docs(document_id, True)
                        Load.replace_placeholders_in_doc(new_document_id,customer_details)

                        result_dict = {
                                "[Route]":str(route),
                                "[Work done]": str(description),
                                "[Obs]":str(obs),
                                "[Exit]":str(exit_units),
                                "[Km]":str(km_units),
                                "[Crane]":str(crane),
                                "[Discharge]":str(discharge_units)
                                }

                        result_dict["[dni]"] = str(" ")
                        result_dict["[price]"] = str(estimation)

                        print(result_dict)
                        Load.replace_placeholders_in_doc(new_document_id,result_dict)
                        Transform.convert_doc_to_pdf_and_save(new_document_id,f"{albaran_id}_{date_str}")
                        # Extract.delete_file_from_google_drive(new_document_id)

                        st.success("¡Guardado con éxito!")

        else:
            st.warning("No se encontraron datos para la compañía seleccionada.")

    elif selected_fields == "Cliente Nuevo":
        company_name = st.text_input("Razón Social:")
        transformed_name = Transform.capital_letters(company_name)

        # Validar si el nombre ya existe
        if transformed_name in names_list and transformed_name:
            st.warning(f"¡La compañía '{transformed_name}' ya existe! Selecciona 'Cliente Habitual'")

            # Disable other fields if the name already exists
            st.text_input("Nombre persona contacto:", disabled=True)
            st.text_input("CIF:", disabled=True)
            st.text_input("Dirección de correo electrónico:", disabled=True)
            st.text_area("Otras direcciones de correo electrónico:", disabled=True)
            st.number_input("Número de teléfono:", step=1, disabled=True, min_value=0)
            st.number_input("Número de teléfono persona de contacto:", disabled=True, min_value=0)
            st.text_input("Dirección:", disabled=True)
            st.number_input("Código postal:", step=1, disabled=True, min_value=0)
            st.text_input("Municipio:", disabled=True)
            st.text_input("Provincia:", disabled=True)
            st.text_input("País:", disabled=True)
            st.number_input("Número de empleados:", step=1, disabled=True, min_value=0)
            st.selectbox("Industria", (
                "AGRICULTURA, SILVICULTURA Y PESCA", "MINERÍA Y CANTERAS", "MANUFACTURAS",
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
                "ACTIVIDADES DE ORGANIZACIONES Y ORGANISMOS EXTRATERRITORIALES"), disabled=True)
            st.date_input("Fecha actual", format="DD/MM/YYYY", disabled=True)
            st.text_area("Información Adicional", disabled=True)

        else:
            # Allow data entry if no match
            contact_name = st.text_input("Nombre persona contacto:")
            cif = st.text_input("CIF:")
            cif = Transform.capital_letters(cif)
            email = st.text_input("Dirección de correo electrónico:")
            other_emails = st.text_area("Otras direcciones de correo electrónico:")
            email_warning = False

            # Validate email format in real-time
            if email and "@" not in email:
                email_warning = True
                st.warning("¡No es una dirección de correo electrónico válida!")

            if not email_warning:
                contact_name = Transform.capital_letters(contact_name)
                email = Transform.lowercase_letters(email)
                other_emails = Transform.lowercase_letters(other_emails)
                phone = st.number_input("Número de teléfono:", step=1, min_value=0,value=None)
                contact_phone = st.number_input("Número de teléfono persona de contacto:",step=1, min_value=0,value=None)
                address = st.text_input("Dirección:")
                address = Transform.capital_letters(address)
                code = st.number_input("Código postal:", step=1, min_value=0,value=None)
                municipality = st.text_input("Municipio:")
                municipality = Transform.capital_letters(municipality)
                city = st.text_input("Provincia:")
                city = Transform.capital_letters(city)
                country = st.text_input("País:")
                country = Transform.capital_letters(country)
                n_employees = st.number_input("Número de empleados:", step=1, min_value=0)
                industry = st.selectbox("Industria", (
                    "AGRICULTURA, SILVICULTURA Y PESCA", "MINERÍA Y CANTERAS", "MANUFACTURAS",
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
                date = st.date_input("Fecha actual", format="DD/MM/YYYY")
                info = st.text_area("Información Adicional")
                info = Transform.capital_letters(info)

                try:

                    # Now calculate the max and ensure it's not NaN
                    albaran_id = Load.generate_albaran_id(albaran)
                except ValueError as e:
                    # Handle the case where the conversion fails entirely
                    print("Error creating albarán_id")


                st.write("""El DNI previsto a continuación y la firma se utilizarán únicamente para la creación del albarán.
                             En ningún caso se almacenarán individualmente, ni se utilizarán para otros fines distintos al anteriormente descrito.
                             La información prevista sobre la empresa, serán utilizados únicamente para mejorar nuestros servicios.""")

                consent = st.checkbox("Acepto")

                # Prepare data for saving
                date_str = date.strftime("%Y-%m-%d")
                ingestion_date = datetime.now()
                ingestion_date_str = ingestion_date.strftime("%Y-%m-%d %H:%M:%S")
                customer_id = str(uuid4())
                version = 1

                if transformed_name and email and phone and address and code and city and country:
                    row_creation = [customer_id, transformed_name, contact_name, cif, email, other_emails, phone, contact_phone,address, code, municipality, city, country, n_employees, industry, date_str, info, version, ingestion_date_str]
                    saving_ready = True
                elif not transformed_name:
                    st.warning("¡Revisa la razón social!")
                    saving_ready = False
                elif not email:
                    st.warning("¡Revisa el correo electrónico!")
                    saving_ready = False
                elif not phone:
                    st.warning("¡Revisa el número de teléfono!")
                    saving_ready = False
                elif not address or not code or not city or not country or not municipality or not country:
                    st.warning("¡Revisa la dirección!")
                    saving_ready = False

                try:
                    df_price_filtered = prices[prices['razón_social'] == company_name]
                    # df_max_p = df_price_filtered.loc[df_price_filtered['versión'].idxmax()]
                    df_max_p = df_price_filtered.loc[ df_price_filtered['versión'].idxmax()]

                    # Reset the index for a clean result if needed
                    df_max_p = df_max_p.reset_index(drop=True)

                except:
                    df_price_filtered = pd.DataFrame()

                if not df_price_filtered.empty:
                    route = st.text_input('Indica la ruta para este trabajo:')
                    route = Transform.capital_letters(route)
                    price_exit_units = float(df_max_p.loc['precio_unidad_salida'])
                    price_km_units = float(df_max_p.loc['precio_kilómetro'])
                    price_crane = float(df_max_p.loc['precio_trabajo_grúa'])
                    price_discharge_units = float(df_max_p.loc['precio_descarga'])
                    price_minimum_service = float(df_max_p.loc['precio_servicio_mínimo'])

                    complete_information_price = True

                    if minimum_service:
                        total_price = price_minimum_service
                    elif not minimum_service:
                        total_price = exit_price * exit_units + km_price * km_units + crane_price * crane + discharge_price * discharge_units
                    st.write(f"Precio estimado:{round(float(total_price),2)}€")
                    estimation = st.radio("¿Estás de acuerdo con este presupuesto?", options=["Sí", "No"])
                    if estimation == "No":
                        estimation = st.number_input("Añade el valor que consideres más acertado", min_value=0.0,step=0.01,value=None)
                    else:
                        estimation = round(total_price,2)

                truck = st.selectbox('Indica el camión que se ha necesitado:', ("Camión 1", "Camión 2", "Camión 3", "Camión 4"), key=f'truck', index=None)
                driver = st.selectbox('Indica el chófer para este trabajo:', ("Chófer 1", "Chófer 2", "Chófer 3"), key='driver', index=None)
                route = st.text_input('Ruta:')
                route = Transform.capital_letters(route)
                exit_units = st.number_input(f'¿Cuántas unidades de salida?',step=1, min_value=0)
                km_units = st.number_input(f'¿Cuántos kilómetros?',step=0.01, min_value=0.0)
                crane = st.number_input(f'¿Cuántas unidades de trabajo de grúa?',step=1, min_value=0)
                discharge_units = st.number_input(f'¿Cuántas unidades de descarga?',step=1, min_value=0)
                minimum_service = st.checkbox("Servicio Mínimo")
                description = st.text_area('Descripción Trabajos realizados:')
                obs = st.text_area(f'Observaciones')


                if driver and truck:
                    row = [str(albaran_id), customer_id, transformed_name, email, route, description,obs,exit_units,
                       km_units, crane, discharge_units, minimum_service, truck, driver, date_str, consent,ingestion_date_str]
                    complete_information = True

                if not driver:
                    st.warning("Selecciona el conductor que ha realizado la tarea.")
                    complete_information = False
                if not truck:
                    st.warning("Selecciona el camión que se ha utilizado en la tarea.")
                    complete_information = False
                if complete_information and complete_information_price:
                    row.append(estimation)

                    # if not minimum_service:
                    #     total_price = price_exit_units * exit_units + price_km_units * km_units + price_crane * crane + price_discharge_units * discharge_units
                    # elif minimum_service:
                    #     total_price = price_exit_units_ms * exit_units + price_km_units_ms * km_units + price_crane_ms * crane + price_discharge_units_ms * discharge_units

                    # if route and price_exit_units and price_km_units and price_crane and price_discharge_units and price_exit_units_ms and price_km_units_ms and price_crane_ms and price_discharge_units_ms:
                    #     complete_information_price = True
                    #     st.write(f"Precio estimado:{round(float(total_price),2)}€")
                    #     estimation = st.radio("¿Estás de acuerdo con este presupuesto?", options=["Sí", "No"])
                    #     if estimation == "No":
                    #             estimation = st.number_input("Añade el valor que consideres más acertado", min_value=0.0,step=0.01)
                    #     else:
                    #         estimation = round(total_price,2)

                    # else:
                    #     complete_information_price = False
                    #     st.warning("Rellena toda la información sobre precios")


                if df_price_filtered.empty:
                    option = st.radio("Este cliente no tiene rango de precios registrado. ¿Quieres añadir un importe estimado de este albarán o añadir todos los precios?", options=["Añadir Manualmente", "Añadir todos los precios"])
                    if option =="Añadir Manualmente":
                        estimation = st.number_input("Añade el importe de este albarán que consideres más acertado", min_value=0.0,step=0.01)
                        if complete_information:
                            row.append(estimation)
                            complete_information_price = False
                    else :
                        exit_price = st.number_input(f"Precio unitario de salida", min_value=0.0,step=0.01,value=None)
                        km_price = st.number_input(f"Precio por kilómetro", min_value=0.0,step=0.01,value=None)
                        crane_price = st.number_input(f"Precio unitario de trabajo de grúa", min_value=0.0,step=0.01,value=None)
                        discharge_price = st.number_input(f"Precio unitario por descarga", min_value=0.0,step=0.01,value=None)
                        minimum_service_price = st.number_input(f"Precio  por servicion mínimo:", min_value=0.0,step=0.01,value=None)
                        customer_id = str(uuid4())
                        version = 1

                        # if route and exit_price and km_price and crane_price and discharge_price and exit_price_ms and km_price_ms and crane_price_ms and discharge_price_ms:
                        #     complete_information_price = True
                        #     row_price = [customer_id, transformed_name,route, exit_price,km_price,crane_price,discharge_price,exit_price_ms,km_price_ms,crane_price_ms,discharge_price_ms, date_str,version]
                        #     if minimum_service:
                        #         total_price = exit_price_ms * exit_units + km_price_ms * km_units + crane_price_ms * crane + discharge_price_ms * discharge_units
                        #     elif not minimum_service:
                        #         total_price = exit_price * exit_units + km_price * km_units + crane_price * crane + discharge_price * discharge_units
                        #     st.write(f"Precio estimado:{round(float(total_price),2)}€")
                        #     estimation = st.radio("¿Estás de acuerdo con este presupuesto?", options=["Sí", "No"])
                        #     if estimation == "No":
                        #         estimation = st.number_input("Añade el valor que consideres más acertado", min_value=0.0,step=0.01)
                        #     else:
                        #         estimation = round(total_price,2)
                        # else:
                        #     complete_information_price = False
                        #     st.warning("Rellena toda la información sobre precios")





                # truck = st.selectbox(f'Indica el camión que se ha necesitado:', ("Camión 1", "Camión 2", "Camión 3", "Camión 4"), key=f'truck', index=None)
                # driver = st.selectbox(f'Indica el chófer para este trabajo:', ("Chófer 1", "Chófer 2", "Chófer 3"), key='driver', index=None)
                # route = st.text_input('Ruta:')
                # route = Transform.capital_letters(route)
                # exit_units = st.number_input(f'¿Cuántas unidades de salida?',step=1)
                # km_units = st.number_input(f'¿Cuántos kilómetros?',step=1)
                # crane = st.number_input(f'¿Cuántas unidades de trabajo de grúa?',step=1)
                # discharge_units = st.number_input(f'¿Cuántas unidades de descarga?',step=1)
                # minimum_service = st.checkbox("Servicio Mínimo")
                # description = st.text_area('Descripción Trabajos realizados:')
                # obs = st.text_area(f'Observaciones')


                # if driver and truck:
                #     row = [str(albaran_id), customer_id, company_name, email, route, description,obs,exit_units,
                #        km_units, crane, discharge_units, minimum_service, truck, driver, date_str, consent,ingestion_date_str,estimation]
                #     complete_information = True

                # if not driver:
                #     st.warning("Selecciona el conductor que ha realizado la tarea.")
                #     complete_information = False
                # if not truck:
                #     st.warning("Selecciona el camión que se ha utilizado en la tarea.")
                #     complete_information = False
                        if exit_price and km_price and crane_price and discharge_price and minimum_service_price:
                                    complete_information_price = True
                                    row_price = [customer_id, transformed_name,route, exit_price,km_price,crane_price,discharge_price,minimum_service_price, date_str,version]
                                    if minimum_service:
                                        total_price = minimum_service_price
                                    elif not minimum_service:
                                        total_price = exit_price * exit_units + km_price * km_units + crane_price * crane + discharge_price * discharge_units
                                    st.write(f"Precio estimado:{round(float(total_price),2)}€")
                                    estimation = st.radio("¿Estás de acuerdo con este presupuesto?", options=["Sí", "No"])
                                    if estimation == "No":
                                        estimation = st.number_input("Añade el valor que consideres más acertado", min_value=0.0,step=0.01,value=None)
                                    else:
                                        estimation = round(total_price,2)
                                    if complete_information:
                                        row.append(estimation)
                        else:
                            complete_information_price = False
                            st.warning("Rellena toda la información sobre precios")





                if consent:
                    dni = st.text_input("Escribe tu DNI:")
                # Create a canvas component
                canvas_result = st_canvas(
                    fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
                    stroke_width=3,#stroke_width,
                    stroke_color='#000',#stroke_color,
                    background_color='White',#bg_color,
                    update_streamlit=True,
                    height=150,
                    drawing_mode="freedraw",
                    point_display_radius= 0,
                    key="app",
                )


                # Form for submission
                with st.form(key='company_form', clear_on_submit=True):
                    submit_button = st.form_submit_button(label='¡Listo!')

                    if submit_button and consent and canvas_result.image_data is not None and complete_information and saving_ready:
                        Load().append_row("Base_de_datos_clientes", "clientes", row_creation)
                        Load().append_row("Base_de_datos_clientes", "albarán", row)
                        if complete_information_price:
                            Load().append_row("Base_de_datos_clientes", "precios unitarios", row_price)

                        customer_details ={
                            "[Date]":str(date_str),
                            "[albarán_id]": str(albaran_id),
                            "[Company]":str(company_name),
                            "[Address]":str(address),
                            "[City]":str(municipality),
                            "[Code]":str(code),
                            "[Cif]":str(cif)
                        }
                        folder_id = st.secrets["folder_id"]

                        document_id = Load.upload_to_drive('template.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ,folder_id,str(transformed_name))
                        Transform.rename_file_in_drive(document_id,albaran_id,date_str)
                        new_document_id = Transform.convert_to_google_docs(document_id, True)
                        Load.replace_placeholders_in_doc(new_document_id,customer_details)

                        result_dict = {
                                "[Route]":str(route),
                                "[Work done]": str(description),
                                "[Obs]":str(obs),
                                "[Exit]":str(exit_units),
                                "[Km]":str(km_units),
                                "[Crane]":str(crane),
                                "[Discharge]":str(discharge_units)
                                }


                        result_dict["[dni]"] = str(dni)
                        result_dict["[price]"] = str(estimation)

                        print(result_dict)
                        Load.replace_placeholders_in_doc(new_document_id,result_dict)
                        image_id, image_link= Load.upload_image_to_google_drive(canvas_result)
                        Load.insert_image_in_document(new_document_id, image_link)
                        Extract.delete_file_from_image_url(image_link)
                        Transform.convert_doc_to_pdf_and_save(new_document_id,f"{albaran_id}_{date_str}")
                        # Extract.delete_file_from_google_drive(new_document_id)

                        st.success("¡Guardado con éxito!")

                    elif submit_button and consent==False and complete_information and saving_ready:
                        Load().append_row("Base_de_datos_clientes", "clientes", row_creation)
                        Load().append_row("Base_de_datos_clientes", "albarán", row)
                        if complete_information_price:
                            Load().append_row("Base_de_datos_clientes", "precios unitarios", row_price)


                        customer_details ={
                            "[Date]":str(date_str),
                            "[albarán_id]": str(albaran_id),
                            "[Company]":str(company_name),
                            "[Address]":str(address),
                            "[City]":str(municipality),
                            "[Code]":str(code),
                            "[Cif]":str(cif)
                        }
                        folder_id = st.secrets["folder_id"]

                        document_id = Load.upload_to_drive('template.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ,folder_id,str(transformed_name))
                        Transform.rename_file_in_drive(document_id,albaran_id,date_str)
                        new_document_id = Transform.convert_to_google_docs(document_id, True)
                        Load.replace_placeholders_in_doc(new_document_id,customer_details)

                        result_dict = {
                                "[Route]":str(route),
                                "[Work done]": str(description),
                                "[Obs]":str(obs),
                                "[Exit]":str(exit_units),
                                "[Km]":str(km_units),
                                "[Crane]":str(crane),
                                "[Discharge]":str(discharge_units)
                                }


                        result_dict["[dni]"] = str(" ")
                        result_dict["[price]"] = str(estimation)

                        print(result_dict)
                        Load.replace_placeholders_in_doc(new_document_id,result_dict)
                        Transform.convert_doc_to_pdf_and_save(new_document_id,f"{albaran_id}_{date_str}")
                        # Extract.delete_file_from_google_drive(new_document_id)

                        st.success("¡Guardado con éxito!")

            else:
                st.warning("No se encontraron datos para la compañía seleccionada.")

# Run the app
if __name__ == "__main__":
    app()
