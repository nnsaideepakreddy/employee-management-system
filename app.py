import streamlit as st
import pandas as pd
import pg8000

def create_db_connection():
    host = "pg-205cff4d-nnsaideepak-adde.g.aivencloud.com"
    database = "defaultdb"
    user = "avnadmin"
    password = "AVNS_sPl-2cVqG3XjT3h_orr"
    port = 21517
    try:
        conn = pg8000.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port,
            ssl_context=True
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None


# Streamlit app title
st.title("Employee Management System (Aiven)")

# Establish a connection to the Aiven PostgreSQL database
conn = create_db_connection()
cursor = None
if conn:
    cursor = conn.cursor()

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
    if cursor:
        try:
            cursor.execute("""
                SELECT E.Name, D.Department_Name, E.Position_Title, I.Insurance_Type, Exp.Year_of_Experience
                FROM Employee E
                JOIN Department D ON E.Department_ID = D.Department_ID
                JOIN Insurance I ON E.Insurance_ID = I.Insurance_ID
                JOIN Experience Exp ON E.Employee_ID = Exp.Employee_ID;
            """)
            rows = cursor.fetchall()
            columns = ["Name", "Department", "Position", "Insurance", "Experience"]
            df = pd.DataFrame(rows, columns=columns)
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error fetching employees: {e}")
    else:
        st.error("No database connection available.")

# Add Employee Page
elif choice == "Add Employee":
    st.subheader("Add New Employee")
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
        if cursor:
            try:
                cursor.execute("""
                    INSERT INTO Employee (Employee_ID, Name, Address, Salary, DOJ, DOB, Age, Sex, Dependents, 
                                         Insurance_ID, Marital_Status_ID, Department_ID, Position_Title)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (employee_id, name, address, salary, doj, dob, age, sex, dependents, insurance_id, marital_status_id, department_id, position_title))
                conn.commit()
                st.success(f"Employee {name} added successfully!")
            except Exception as e:
                st.error(f"Error adding employee: {e}")
        else:
            st.error("No database connection available.")

# Delete Employee Page
elif choice == "Delete Employee":
    st.subheader("Delete Employee")
    employee_id = st.number_input("Employee ID to Delete", min_value=1, step=1)

    if st.button("Delete Employee"):
        if cursor:
            try:
                cursor.execute("DELETE FROM Employee WHERE Employee_ID = %s", (employee_id,))
                conn.commit()
                st.success(f"Employee with ID {employee_id} deleted successfully!")
            except Exception as e:
                st.error(f"Error deleting employee: {e}")
        else:
            st.error("No database connection available.")

# Update Employee Page
elif choice == "Update Employee":
    st.subheader("Update Employee Salary")
    employee_id = st.number_input("Employee ID to Update", min_value=1, step=1)
    new_salary = st.number_input("New Salary", min_value=0.0, step=0.01)

    if st.button("Update Salary"):
        if cursor:
            try:
                cursor.execute("UPDATE Employee SET Salary = %s WHERE Employee_ID = %s", (new_salary, employee_id))
                conn.commit()
                st.success(f"Employee with ID {employee_id} updated successfully!")
            except Exception as e:
                st.error(f"Error updating employee: {e}")
        else:
            st.error("No database connection available.")

# Department Analytics Page
elif choice == "Department Analytics":
    st.subheader("Department Analytics")
    if cursor:
        try:
            cursor.execute("""
                SELECT D.Department_Name, COUNT(E.Employee_ID) AS Number_of_Employees
                FROM Employee E
                JOIN Department D ON E.Department_ID = D.Department_ID
                GROUP BY D.Department_Name;
            """)
            rows = cursor.fetchall()
            columns = ["Department", "Number of Employees"]
            df = pd.DataFrame(rows, columns=columns)
            # Create a bar chart for department analytics
            st.bar_chart(df.set_index("Department"))
        except Exception as e:
            st.error(f"Error fetching department analytics: {e}")
    else:
        st.error("No database connection available.")

# View All Tables Page
elif choice == "View All Tables":
    st.subheader("View All Tables")
    table_choice = st.selectbox("Select Table", ["Department", "Insurance", "Marital_Status", "Employee", "Compensation", "Experience", "Main"])
    if st.button("Show Table"):
        if cursor:
            try:
                cursor.execute(f"SELECT * FROM {table_choice};")
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(rows, columns=columns)
                st.dataframe(df)
            except Exception as e:
                st.error(f"Error fetching table data: {e}")
        else:
            st.error("No database connection available.")

# Close the database connection
if conn:
    cursor.close()
    conn.close()
