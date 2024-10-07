import pydicom
from pydicom.dataset import Dataset
import os
import uuid

def deidentify_dicom(input_folder, output_folder):
    # 입력 폴더에서 모든 DICOM 파일을 순회
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.dcm'):
                file_path = os.path.join(root, file)
                
                # DICOM 파일 읽기
                ds = pydicom.dcmread(file_path)

                # 비식별화 작업 수행
                # 직접 식별자 (환자 이름, ID 등)
                ds.PatientName = "Anon_" + str(uuid.uuid4())[:8]  # 임의의 가명으로 대체
                ds.PatientID = str(uuid.uuid4())[:8]
                ds.PatientBirthDate = "19000101"  # 생년월일을 특정 값으로 대체
                
                # 간접 식별자 (주소, 의사 이름 등)
                if 'PatientAddress' in ds:
                    ds.PatientAddress = "Anonymized"
                if 'ReferringPhysicianName' in ds:
                    ds.ReferringPhysicianName = "Anonymized"

                # UID 재생성 - StudyInstanceUID와 SeriesInstanceUID 재설정
                ds.StudyInstanceUID = pydicom.uid.generate_uid()
                ds.SeriesInstanceUID = pydicom.uid.generate_uid()
                ds.SOPInstanceUID = pydicom.uid.generate_uid()

                # 기타 민감 정보 제거
                sensitive_tags = [
                    (0x0010, 0x2154),  # Patient's Telephone Numbers
                    (0x0008, 0x0090),  # Referring Physician's Name
                    (0x0010, 0x0030),  # Patient's Birth Date
                    (0x0010, 0x1040),  # Patient's Address
                ]
                for tag in sensitive_tags:
                    if tag in ds:
                        del ds[tag]

                # 출력 폴더에 비식별화된 DICOM 파일 저장
                output_path = os.path.join(output_folder, file)
                ds.save_as(output_path)
                print(f"De-identified: {file_path} -> {output_path}")

# 사용 예시
input_folder = "input_dicom_files"  # 원본 DICOM 파일들이 있는 폴더
output_folder = "output_dicom_files"  # 비식별화된 DICOM 파일들을 저장할 폴더

# 출력 폴더가 없으면 생성
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

deidentify_dicom(input_folder, output_folder)
