# Doctor-Assistant

## Project Description
This is a doctor assistant project developed using Langflow to help doctors quickly retrieve information. The main functionalities include:
- Search for Wikipedia information
- Search for files uploaded by the doctor
- Control the query source (Wikipedia or doctor-uploaded files)
- Uploaded files can be stored in different databases for better categorization and management
- Control which database to search from via the conversation interface

## Key Features
- **Search Wikipedia Information**: Quickly query and return relevant information from Wikipedia.
- **Search Uploaded Files**: Doctors can upload their own files to different databases, and the assistant can search through these files.
- **Database Management**: The assistant supports multiple databases and allows selecting which database to query from in the conversation interface.

## Technologies Used
- **Langflow**: A visual workflow-building tool used to define and manage the project flow.
- **AstraDB**: Used to store and manage the doctor's uploaded files, supporting various file formats and data retrieval functions.
- **OpenAI**: Powers natural language dialogue, providing intelligent querying and interaction capabilities.

## How to Use
1. Upload the doctor's files to the system and select the appropriate database for storage.
2. In the query interface, you can choose the source of the data, either Wikipedia or the uploaded files.
3. The system will return the relevant data based on the selected source.


## Demo
### Flow Diagram
Here is the visual representation of the flow used in this project, built with Langflow:
![image](https://github.com/RianneTseng/Doctor-Assistant/blob/main/Flow%20Diagram.png)

### Functionality Demo

#### 1. Searching Wikipedia Information
![image](https://github.com/RianneTseng/Doctor-Assistant/blob/main/Searching%20Wikipedia%20Information.png)

#### 2. Searching Uploaded Files
![image](https://github.com/RianneTseng/Doctor-Assistant/blob/main/Searching%20Uploaded%20Files.png)

#### 3. Simultaneous Search (Wikipedia + Uploaded Files)
![image](https://github.com/RianneTseng/Doctor-Assistant/blob/main/Simultaneous%20Search.png)

#### 4. Switching Data Sources
In the Folder option from this image, you can input different database names to switch between different databases.
![image](https://github.com/RianneTseng/Doctor-Assistant/blob/main/Switching%20Data%20Sources.png)

#### 5. Managing Multiple Databases
![image](https://github.com/RianneTseng/Doctor-Assistant/blob/main/Managing%20Multiple%20Databases.png)


## Project Files
- `doctor.json`: A flow file exported from Langflow.
- `README.md`: Documentation and project notes.
