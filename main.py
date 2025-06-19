from fastapi import FastAPI , HTTPException , Path , Query
import json
from pydantic import BaseModel , Field , computed_field , field_validator
from fastapi.responses import JSONResponse
from typing import Optional , Annotated , Literal
app = FastAPI()

from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal

app = FastAPI()

class Patient(BaseModel):
    id: str = Field(..., description='ID of the patient')
    name: str = Field(..., description='Name of the patient')
    city: str = Field(..., description='City of the patient')
    age: int = Field(..., gt=0, lt=120, description='Age of the patient')
    gender: Literal['male', 'female'] = Field(..., description='Gender of the patient')
    height: float = Field(..., gt=0, description='Height in meters')
    weight: float = Field(..., gt=0, description='Weight in kgs')

    @property
    def BMI(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    @property
    def verdict(self) -> str:
        if self.BMI < 18.5:
            return 'Underweight'
        elif self.BMI < 25:
            return 'Normal'
        elif self.BMI < 30:
            return 'Overweight'
        else:
            return 'Obese'

    @field_validator('city')
    @classmethod
    def normalize_city(cls, city: str) -> str:
        return city.strip().title()



class UpdatePatient(BaseModel):
    name: Optional[str] = Field(None, description='Name of the patient')
    city: Optional[str] = Field(None, description='City of the patient')
    age: Optional[int] = Field(None, gt=0, lt=120, description='Age of the patient')
    gender: Optional[Literal['male', 'female']] = Field(None, description='Gender of the patient')
    height: Optional[float] = Field(None, gt=0, description='Height in meters')
    weight: Optional[float] = Field(None, gt=0, description='Weight in kgs')


def load_data():
    with open('patients.json' , 'r') as f:
        data = json.load(f)
        return data
    
def save_data(file):
    with open('patients.json' , 'w') as f:
        return json.dump(file , f)



@app.get('/home')
def home():
    data = load_data()
    return data

@app.get('/find/{patient_id}')
def home1(patient_id : str):
    data = load_data()
    if patient_id not in data:
        HTTPException(status_code=404 , detail='Id not found')
    else:
        output = data[patient_id] 
        return output

@app.get('/sort')
def sort(sort_by : str = Query(default=None , description='weight/height/bmi'), 
    order_by :str = Query(default='asc' , description='asc/desc')):
    columns = ['weight' , 'height' , 'bmi']
    data = load_data()
    if sort_by not in columns:
        HTTPException(status_code=404 , detail='column invalid')
    else:
        order = True if order_by == 'desc' else False
        sorted_data = sorted(data.values() , key = lambda x : x.get(sort_by , 0) , reverse=order)
        return sorted_data
    
@app.post('/create')
def create(data1 : Patient):
    data = load_data()
    if data1.id in data:
        raise HTTPException(status_code=201 , detail='already exists')
    else:
        data[data1.id] = data1.model_dump(exclude={'id'})
        save_data(data)
        return {"message": "Patient created successfully", "patient_id": data1.id}
    

@app.post('/update/{patient_id}')
def update(patient_id: str, data1: UpdatePatient):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='ID not found')

    updated_fields = data1.model_dump(exclude_unset=True)
    existing_patient = data[patient_id]

    for key, value in updated_fields.items():
        existing_patient[key] = value

    existing_patient['id'] = patient_id  # Re-set the ID if needed

    # Validate with Pydantic model
    pydantic_obj = Patient(**existing_patient)
    data[patient_id] = pydantic_obj.model_dump(exclude={'id'})

    save_data(data)
    return JSONResponse(status_code=203, content={"message": "Updated successfully"})

    
@app.delete('/delete/{patient_id}')
def delete(patient_id : str):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404 , detail='id not found')
    else:
        del data[patient_id]
        save_data(data)