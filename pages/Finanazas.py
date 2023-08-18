import streamlit as st
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import pathlib
import PyPDF2
from pdf2image import convert_from_path
from PIL import Image
# Configuración de Azure Blob Storage
azure_connection_string = os.getenv("AZURE_ENDPOINT")
container_name = "raw"

def get_blob_url(blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    return blob_client.url



def upload_to_azure_blob(file_path, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    
    with open(file_path, "rb") as data:
        container_client.upload_blob(blob_name, data, overwrite=True)


endpoint = "https://eastus2.api.cognitive.microsoft.com/"
key = os.getenv("OPENAI_API_KEY")



def main():
    col1,col2,col3 = st.columns(3)
    container = st.container()
    image = Image.open('logo.png')
    with container:
        col2.image(image, use_column_width=False)

    st.title("OPENAI Demo - CENTRIA")
    uploaded_file = st.file_uploader("Selecciona un archivo PDF", type=["PDF"])
    if uploaded_file is not None:
        st.write("Archivo cargado:", uploaded_file.name)
        if "image" in st.session_state and st.session_state["image"] != '' and st.session_state["image"] is not None:
            st.image(st.session_state["image"])

        
        if btn_0:
            bytes_data = uploaded_file.getvalue()
            data = uploaded_file.getvalue()
            
            parent_path = pathlib.Path(__file__).parent.parent.resolve()           
            save_path = os.path.join(parent_path, "../CENTRIA/data")
            complete_name = os.path.join(save_path, uploaded_file.name)
            with open(complete_name, "wb") as f:
                f.write(bytes_data)
            st.session_state["upload_state"] = complete_name
            pdf_file = open(st.session_state["upload_state"], 'rb')
            read_pdf = PyPDF2.PdfReader(pdf_file)
            number_of_pages = len(read_pdf.pages)
            #for i in range(number_of_pages):
            page = read_pdf.pages[1]
            #img = read_pdf.pages[1].images
            img = convert_from_path('data/'+uploaded_file.name, 500)[0]
            img.save('img'+str(20)+'.jpg', 'JPEG')
            st.success("Archivo Formateado exitosamente")
            
            
        if btn_1:
            uploaded_file = open('img'+str(20)+'.jpg', 'rb')
            file_path = os.path.join("temp_files", 'img'+str(20)+'.jpg')#uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
            
            blob_name = 'img'+str(20)+'.jpg'#uploaded_file.name
            upload_to_azure_blob(file_path, blob_name)
            blob_url = get_blob_url(blob_name)
            st.session_state["blob_url"] = blob_url
            st.write(blob_url)
            st.success("Archivo subido exitosamente a Azure Blob Storage")
            st.write("Nombre del archivo:", blob_name)
            image = Image.open(file_path)
            st.session_state["image"] = image
            
            os.remove(file_path)  # Eliminar el archivo temporal

        if btn_2:
            if st.session_state["blob_url"] != '' and st.session_state["blob_url"] is not None:
                blob_url = str(st.session_state["blob_url"])
                
                formUrl = blob_url # "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/invoice_sample.jpg"
                st.success(formUrl)
                document_analysis_client = DocumentAnalysisClient(
                    endpoint=endpoint, credential=AzureKeyCredential(key)
                    )
                    
                poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-invoice", formUrl)
                invoices = poller.result()
                # print(invoices)

                for idx, invoice in enumerate(invoices.documents):
                    st.write("--------Recognizing invoice #{}--------".format(idx + 1))
                    vendor_name = invoice.fields.get("VendorName")
                    if vendor_name:
                        valor = ("Vendor Name: {} has confidence: {}").format(vendor_name.value, vendor_name.confidence)
                        st.write(valor)
                        
                    vendor_address = invoice.fields.get("VendorAddress")
                    if vendor_address:
                        valor = ("Vendor Address: {} has confidence: {}").format(vendor_address.value, vendor_address.confidence)
                        st.write(valor)

                    vendor_address_recipient = invoice.fields.get("VendorAddressRecipient")
                    if vendor_address_recipient:
                        valor = ("Vendor Address Recipient: {} has confidence: {}").format(vendor_address_recipient.value, vendor_address_recipient.confidence)
                        st.write(valor)
                        
                    customer_name = invoice.fields.get("CustomerName")
                    if customer_name:
                        valor = ("Customer Name: {} has confidence: {}").format(customer_name.value, customer_name.confidence)
                        st.write(valor)

                    customer_address = invoice.fields.get("CustomerAddress")
                    if customer_address:
                        valor = ("Customer Address: {} has confidence: {}").format(customer_address.value, customer_address.confidence)
                        st.write(valor)

                    customer_address_recipient = invoice.fields.get("CustomerAddressRecipient")
                    if customer_address_recipient:
                        valor = ("Customer Address Recipient: {} has confidence: {}").format(customer_address_recipient.value, customer_address_recipient.confidence)
                        st.write(valor)

                    invoice_id = invoice.fields.get("InvoiceId")
                    if invoice_id:
                        valor = ("Invoice Id: {} has confidence: {}").format(invoice_id.value, invoice_id.confidence)
                        st.write(valor)

                    invoice_date = invoice.fields.get("InvoiceDate")
                    if invoice_date:
                        valor = ("Invoice Date: {} has confidence: {}").format(invoice_date.value, invoice_date.confidence)
                        st.write(valor)

                    invoice_total = invoice.fields.get("InvoiceTotal")
                    if invoice_total:
                        valor = ("Invoice Total: {} has confidence: {}").format(invoice_total.value, invoice_total.confidence)
                        st.write(valor)

                    due_date = invoice.fields.get("DueDate")
                    if due_date:
                        valor = ("Due Date: {} has confidence: {}").format(due_date.value, due_date.confidence)
                        st.write(valor)

                    for idx, item in enumerate(invoice.fields.get("Items").value):
                        st.write("...Item #{}".format(idx + 1))
                        item_description = item.value.get("Description")
                        if item_description:
                            st.write(
                                "......Description: {} has confidence: {}".format(
                                    item_description.value, item_description.confidence
                                )
                            )
                        item_quantity = item.value.get("Quantity")
                        if item_quantity:
                            st.write(
                                "......Quantity: {} has confidence: {}".format(
                                    item_quantity.value, item_quantity.confidence
                                )
                            )
                        unit = item.value.get("Unit")
                        if unit:
                            st.write(
                                "......Unit: {} has confidence: {}".format(
                                    unit.value, unit.confidence
                                )
                            )
                        unit_price = item.value.get("UnitPrice")
                        if unit_price:
                            st.write(
                                "......Unit Price: {} has confidence: {}".format(
                                    unit_price.value, unit_price.confidence
                                )
                            )
                        product_code = item.value.get("ProductCode")
                        if product_code:
                            st.write(
                                "......Product Code: {} has confidence: {}".format(
                                    product_code.value, product_code.confidence
                                )
                            )
                        item_date = item.value.get("Date")
                        if item_date:
                            st.write(
                                "......Date: {} has confidence: {}".format(
                                    item_date.value, item_date.confidence
                                )
                            )
                        tax = item.value.get("Tax")
                        if tax:
                            st.write(
                                "......Tax: {} has confidence: {}".format(tax.value, tax.confidence)
                            )
                        amount = item.value.get("Amount")
                        if amount:
                            st.write(
                                "......Amount: {} has confidence: {}".format(
                                    amount.value, amount.confidence
                                )
                            )
                    subtotal = invoice.fields.get("SubTotal")
                    if subtotal:
                        st.write(
                            "Subtotal: {} has confidence: {}".format(
                                subtotal.value, subtotal.confidence
                            )
                        )
                    total_tax = invoice.fields.get("TotalTax")
                    if total_tax:
                        st.write(
                            "Total Tax: {} has confidence: {}".format(
                                total_tax.value, total_tax.confidence
                            )
                        )
                    previous_unpaid_balance = invoice.fields.get("PreviousUnpaidBalance")
                    if previous_unpaid_balance:
                        st.write(
                            "Previous Unpaid Balance: {} has confidence: {}".format(
                                previous_unpaid_balance.value, previous_unpaid_balance.confidence
                            )
                        )
                    amount_due = invoice.fields.get("AmountDue")
                    if amount_due:
                        st.write(
                            "Amount Due: {} has confidence: {}".format(
                                amount_due.value, amount_due.confidence
                            )
                        )

btn_0 = st.sidebar.button("Format Document")
btn_1 = st.sidebar.button("Subir a Azure Blob Storage")
btn_2 = st.sidebar.button("Analizar")
                    

            
if __name__ == "__main__":
    main()
