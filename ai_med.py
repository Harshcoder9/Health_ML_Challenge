import os
import json
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
from sentence_transformers import SentenceTransformer
from langchain_core.vectorstores import InMemoryVectorStore
import numpy as np
from collections import defaultdict

# token
# google_token = json.loads(open("tkn.json", "r").read())["google_tkn"]

# creating patient database list
patient_detail_path = "Patient_Details"
patient_list = []
for patient_file in os.listdir(patient_detail_path):
    per_patient_detail = {}
    file = open(os.path.join(patient_detail_path, patient_file), "r")
    for line in file.readlines():
        if line.startswith("Patient_ID"):
            per_patient_detail["patient_id"] = line.split(":")[1].strip()
        if line.startswith("Age"):
            per_patient_detail["age"] = line.split(":")[1].strip()
        if line.startswith("Gender"):
            per_patient_detail["gender"] = line.split(":")[1].strip()
    file = open(os.path.join(patient_detail_path, patient_file), "r")
    for section in file.read().split("--- "):
        if section.startswith("Symptoms"):
            per_patient_detail["symptoms"] = section.split(
                "---")[1].strip().replace("\n", ", ")
        if section.startswith("Vitals"):
            per_patient_detail["vitals"] = section.split(
                "---")[1].strip().replace("\n", ", ")
        if section.startswith("Lab Reports"):
            per_patient_detail["lab_reports"] = section.split(
                "---")[1].strip().replace("\n", ", ")
        if section.startswith("Doctor Notes"):
            per_patient_detail["doctor_notes"] = section.split(
                "---")[1].strip().replace("\n", " ")
        if section.startswith("Final Department"):
            per_patient_detail["final_department"] = section.split(
                "---")[1].strip().replace("\n", " ")
        if section.startswith("Outcome"):
            per_patient_detail["outcome"] = section.split(
                "---")[1].strip().replace("\n", " ")
    patient_list.append(per_patient_detail)

# print(patient_list)
print("---Patient List---")
print(patient_list[0])

# creating chunks
chunks = []
for patient in patient_list:
    chunks.append({
        "text": f"Symptoms: {patient['symptoms']}",
        "metadata": {
            "patient_id": patient["patient_id"],
            "chunk_type": "symptoms",
            "department": patient["final_department"]
        }
    })
    chunks.append({
        "text": f"Vitals: {patient['vitals']}\nLab results: {patient['lab_reports']}",
        "metadata": {
            "patient_id": patient["patient_id"],
            "chunk_type": "clinical",
            "department": patient["final_department"]
        }
    })
    chunks.append({
        "text": f"Doctor Assesment: {patient['doctor_notes']}",
        "metadata": {
            "patient_id": patient["patient_id"],
            "chunk_type": "assessment",
            "department": patient["final_department"]
        }
    })

# print(chunks)
print("---Chunks---")
print(chunks[0:4])

# creating embedding
# embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=google_token)
embeddings = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

vector_store = []

for chunk in chunks:
    vector_store.append({
        "embedding": embeddings.encode(chunk["text"]),
        "text": chunk["text"],
        "metadata": chunk["metadata"]
    })

print("---vector store---")
# print(vector_store[0])

# retrieval


def query_embedding(query_text):
    return embeddings.encode(query_text)


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def retrieve(query_text, top_k):
    results = sorted(
        vector_store,
        key=lambda x: cosine_similarity(
            query_embedding(query_text), x["embedding"]),
        reverse=True
    )

    top_chunks = results[:top_k]

    return top_chunks

# executor


def executor(query_text):

    retrv = retrieve(query_text, 6)

    patient_groups = defaultdict(list)
    for r in retrv:
        patient_groups[r["metadata"]["patient_id"]].append(r)

    highest_similarity_patient = ""
    highest_similarity_patient_department = ""
    c = 0
    for pat_id in patient_groups.keys():
        if len(patient_groups[pat_id]) > c:
            highest_similarity_patient, highest_similarity_patient_department = pat_id, patient_groups[
                pat_id][0]["metadata"]["department"]
            c = len(patient_groups[pat_id])

    print("---highest similarity patient and highest similarity patient department---")
    print("highest_similarity_patient: ", highest_similarity_patient,
          ", highest_similarity_patient_department: ", highest_similarity_patient_department)

    # getting hospital list, doctors and available slots
    hospital_list = json.loads(
        open(os.path.join("Hospital_Details", "hospital_list.json")).read())

    selected_hospitals = []
    for hospital in hospital_list:
        if highest_similarity_patient_department in hospital["department"]:
            selected_hospitals.append(hospital["hospital"])

    print("---selected hospitals---")
    print(selected_hospitals)

    selected_hospitals_doctors = []
    for hospital in selected_hospitals:
        specific_hospital = {}
        specific_hospital["hospital_name"] = hospital
        specific_hospital["department"] = highest_similarity_patient_department
        file_content = json.loads(open(os.path.join(
            "Hospital_Details", "hospital_" + hospital.lower() + ".json")).read())
        for department in file_content:
            if department["Department"] == highest_similarity_patient_department:
                specific_hospital["doctor_time_slots"] = department["Doctor_List"]
                # Add Directions_Link if present
                if "Directions_Link" in department:
                    specific_hospital["Directions_Link"] = department["Directions_Link"]
                break
        selected_hospitals_doctors.append(specific_hospital)

    print("---selected hospital doctors---")
    print(selected_hospitals_doctors)

    report_summary = generate_report_summary(
        query_text,
        highest_similarity_patient_department
    )
    report_summary_hindi = generate_report_summary_hindi(
        query_text,
        highest_similarity_patient_department
    )

    return {
        "recommended_hospitals": selected_hospitals_doctors,
        "report_summary_en": report_summary,          # English
        "report_summary_hi": report_summary_hindi     # Hindi
    }


def generate_report_summary(query_text, department):
    q = query_text.lower()
    points = []

    # Symptom based points
    if "fever" in q:
        points.append("Fever indicates a possible infection or inflammation.")

    if "cough" in q:
        points.append("Cough suggests involvement of the respiratory system.")

    if "headache" in q:
        points.append(
            "Headache can occur due to infection, stress, or dehydration.")

    if "chest pain" in q:
        points.append(
            "Chest pain may be associated with cardiac or respiratory conditions.")

    if "shortness of breath" in q:
        points.append(
            "Breathing difficulty can indicate lung or heart-related issues.")

    # Generic reasoning
    points.append(
        f"Based on similar past patient cases, consultation with the {department} department is advised."
    )

    points.append(
        "Hospital recommendations are provided based on department availability and past outcomes."
    )

    return points


def generate_report_summary_hindi(query_text, department):
    q = query_text.lower()
    points = []

    if "fever" in q or "बुखार" in q:
        points.append(
            "बुखार आमतौर पर किसी संक्रमण या सूजन का संकेत हो सकता है।")

    if "cough" in q or "खांसी" in q:
        points.append(
            "खांसी से यह संकेत मिलता है कि सांस से जुड़ी समस्या हो सकती है।")

    if "headache" in q or "सिर दर्द" in q:
        points.append(
            "सिर दर्द संक्रमण, कमजोरी या डिहाइड्रेशन के कारण हो सकता है।")

    if "chest pain" in q:
        points.append(
            "छाती में दर्द हृदय या फेफड़ों से संबंधित समस्या का संकेत हो सकता है।")

    if "shortness of breath" in q:
        points.append(
            "सांस लेने में तकलीफ फेफड़ों या हृदय की समस्या से जुड़ी हो सकती है।")

    points.append(
        f"पिछले समान मरीजों के आधार पर, इस स्थिति में {department} विभाग से परामर्श की सलाह दी जाती है।"
    )

    points.append(
        "इसी जानकारी के आधार पर उपयुक्त अस्पताल और डॉक्टरों की सिफारिश की गई है।"
    )

    return points


if __name__ == "__main__":
    query_text = """Symptoms: fever, cough, headache"""
    print(executor(query_text))
