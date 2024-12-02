import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# Database connection settings
@st.cache_resource
def create_db_connection():
    db_url = "postgresql+pg8000://postgres:2495@localhost:5432/Project"
    engine = create_engine(db_url)
    return engine.connect()

# Streamlit app title
st.title("Employee Management System")

# Establish a connection to PostgreSQL database
conn = create_db_connection()

# Sidebar menu options
menu = ["Home", "View Employees", "Add Employee", "Delete Employee", "Update Employee", "Department Analytics", "View All Tables"]
choice = st.sidebar.selectbox("Menu", menu)

# Home Page
if choice == "Home":
    st.subheader("Welcome to the Employee Management System")
    st.write("Use the sidebar to navigate through the options.")

# View Employees Page
elif choice == "View Employees":
    st.subheader("View All Employees")
    query = """
        SELECT E.Name, D.Department_Name, E.Position_Title, I.Insurance_Type, Exp.Year_of_Experience
        FROM Employee E
        JOIN Department D ON E.Department_ID = D.Department_ID
        JOIN Insurance I ON E.Insurance_ID = I.Insurance_ID
        JOIN Experience Exp ON E.Employee_ID = Exp.Employee_ID
    """
    result = conn.execute(text(query))
    rows = result.fetchall()
    columns = ["Name", "Department", "Position", "Insurance", "Experience"]
    df = pd.DataFrame(rows, columns=columns)
    st.dataframe(df)

# Add Employee Page
elif choice == "Add Employee":
    st.subheader("Add New Employee")
    # Input fields to add a new employee
    employee_id = st.number_input("Employee ID", min_value=1, step=1)
    name = st.text_input("Name")
    address = st.text_area("Address")
    salary = st.number_input("Salary", min_value=0.0, step=0.01)
    doj = st.date_input("Date of Joining")
    dob = st.date_input("Date of Birth")
    age = st.number_input("Age", min_value=18, step=1)
    sex = st.selectbox("Gender", ["Male", "Female", "Other"])
    dependents = st.number_input("Dependents", min_value=0, step=1)
    department_id = st.number_input("Department ID", min_value=1, step=1)
    position_title = st.text_input("Position Title")
    insurance_id = st.number_input("Insurance ID", min_value=1, step=1)
    marital_status_id = st.number_input("Marital Status ID", min_value=1, step=1)

    if st.button("Add Employee"):
        try:
            query = """
                INSERT INTO Employee (Employee_ID, Name, Address, Salary, DOJ, DOB, Age, Sex, Dependents, 
                                      Insurance_ID, Marital_Status_ID, Department_ID, Position_Title)
                VALUES (:employee_id, :name, :address, :salary, :doj, :dob, :age, :sex, :dependents, 
                        :insurance_id, :marital_status_id, :department_id, :position_title)
            """
            conn.execute(text(query), {
                'employee_id': employee_id,
                'name': name,
                'address': address,
                'salary': salary,
                'doj': doj,
                'dob': dob,
                'age': age,
                'sex': sex,
                'dependents': dependents,
                'insurance_id': insurance_id,
                'marital_status_id': marital_status_id,
                'department_id': department_id,
                'position_title': position_title
            })
            st.success(f"Employee {name} added successfully!")
        except Exception as e:
            st.error(f"Error adding employee: {e}")

# Delete Employee Page
elif choice == "Delete Employee":
    st.subheader("Delete Employee")
    employee_id = st.number_input("Employee ID to Delete", min_value=1, step=1)

    if st.button("Delete Employee"):
        try:
            query = "DELETE FROM Employee WHERE Employee_ID = :employee_id"
            conn.execute(text(query), {'employee_id': employee_id})
            st.success(f"Employee with ID {employee_id} deleted successfully!")
        except Exception as e:
            st.error(f"Error deleting employee: {e}")

# Update Employee Page
elif choice == "Update Employee":
    st.subheader("Update Employee Salary")
    employee_id = st.number_input("Employee ID to Update", min_value=1, step=1)
    new_salary = st.number_input("New Salary", min_value=0.0, step=0.01)

    if st.button("Update Salary"):
        try:
            query = "UPDATE Employee SET Salary = :new_salary WHERE Employee_ID = :employee_id"
            conn.execute(text(query), {'new_salary': new_salary, 'employee_id': employee_id})
            st.success(f"Employee with ID {employee_id} updated successfully!")
        except Exception as e:
            st.error(f"Error updating employee: {e}")

# Department Analytics Page
elif choice == "Department Analytics":
    st.subheader("Department Analytics")
    # Query for department-wise employee count
    query = """
        SELECT D.Department_Name, COUNT(E.Employee_ID) AS Number_of_Employees
        FROM Employee E
        JOIN Department D ON E.Department_ID = D.Department_ID
        GROUP BY D.Department_Name
    """
    result = conn.execute(text(query))
    rows = result.fetchall()
    columns = ["Department", "Number of Employees"]
    df = pd.DataFrame(rows, columns=columns)
    st.bar_chart(df.set_index("Department"))

# View All Tables Page
elif choice == "View All Tables":
    st.subheader("View All Tables")
    table_choice = st.selectbox("Select Table", ["Department", "Insurance", "Marital_Status", "Employee", "Compensation", "Experience", "Main"])
    if st.button("Show Table"):
        try:
            query = f"SELECT * FROM {table_choice}"
            result = conn.execute(text(query))
            rows = result.fetchall()
            columns = [desc[0] for desc in result.cursor.description]
            df = pd.DataFrame(rows, columns=columns)
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error fetching table data: {e}")

# Close the database connection
conn.close()
