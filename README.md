#   BFB Semester Project - Supply Chain Web Appliaction

This project is a **web-based logistics management system** developed for BFB321. 
It enables users to manage **drivers, trucks, deliveries, odometer logs, and maintenance records** through a simple HTML/CSS interface with a supporting SQL schema.

---
## Team Details

| Student Number | Name      | Surname      | Username           |
|:---------------|:----------|:-------------|:-------------------|
| 22517741       | Alexander | Michael      | AlexanderMicheal12 |
| 22543725       | Dimitri   | Ladas        | DimitriLadas       |
| 22550292       | Jarod     | Labuschagne  | Jarod2507025       |
| 23529939       | Leandro   | Pimentel     | Leandro01789       |

---
## Task allocation

- Alexander Michael
Led the REST API design, defined all backend endpoints, and implemented the core backend logic together with database integration. Also authored the Reflection section of the final report.

- Dimitri Ladas
Created the entire project README from scratch and produced the Implementation Guide. Completed the Risk & Mitigation section as well as the Sustainability & Scalability components of the report.

- Jarod Labuschagne
Authored the Executive Summary and the Final Concept & System Architecture sections. Assisted with frontend–backend integration to ensure smooth communication between UI and backend services.

- Leandro Pimentel
Developed key components of the backend logic, contributed extensively to database integration, and supported frontend–backend integration. Authored the Technology Integration and User Journey sections of the report.

---
## Overview
The system provides:
- A dashboard linking all main modules
- HTML pages for drivers, vehicles and delivery history
- A shared CSS file for consistent styling
- An SQL schema and demo database to support backend integration in the future

**Tech Stack**
- Frontend: HTML, CSS
- Data Layer: SQL schema (`TruckDelivery.sql`) + SQLite demo DB (`TruckDelivery.db`)

---

## Features
- **Dashboard (`home.html`, `index.html`)**
  Landing page with navigation to different modules.
- **Driver Management (`drivers.html`)**
  List of drivers with contact details and assigned vehicles.
- **Individual Vehicle Management (`vehicle.html`)**
  Displays vehicle specific information including service records, live vehicle tracking and useful metrics.
- **Delivery History (`history.html`)**
  Records of completed deliveries.
- **Styling (`main.css`)**
  Consistent styles for tables, navigation, and layout.
- **Database Support (`TruckDelivery.sql`, `TruckDelivery.db`)**
  Schema and example database for drivers, trucks, deliveries, odometer logs, and maintenance logs.

---

## System Design

### Entity Relationship Diagram (ERD)

<img width="730" height="851" alt="ERD" src="https://github.com/user-attachments/assets/5239181d-5541-482f-a08c-f7be0488ce2a" />

### Tables 
1. **drivers**: Stores driver details (name, phone, assigned truck).
2. **trucks**: Information about each truck (code, license plate).
3. **deliveries**: Records of deliveries with pickup/drop-off info and status. 
4. **maintenance_logs**: History of maintenance done on trucks.
5. **odometer_logs**: Mileage records for trucks over time. 

### Sample Data
The database includes sample entries for testing: 
- Drivers with phone numbers and assigned trucks.
- Trucks with codes and license plates.
- Delivery records with statuses (Pending, In Transit, Delivered).
- Example maintenance logs and odometer readings.

## File Structure
```
├─ .venv/                 # Virtual environment
│
├─ static/
│  └─ main.css            # Global stylesheets
│
├─ templates/
│  ├─ drivers.html        # Driver contacts details
│  ├─ history.html        # Fleet history
│  ├─ home.html           # Main dashboard
│  ├─ index.html          # Login page
│  └─ vehicle.html        # Vehicle specifc dashboard & stats
│
├─ README.md              # Project documentation
├─ TruckDelivery.db       # SQLite database
├─ TruckDelivery.sql      # Database schema
└─ app.py                 # Flask application
```
## Usage

1. Open the project folder in VS Code.
2. Double-click the `index.html` and the web browser will open up.
3. Navigate the different pages to manage the drivers and trucks or view the overall company history.

## Technologies Used

- **HTML5**: Structure and static pages.
- **CSS3**: Styling and responsive layout.
- **Bootstrap Icons**: Icon set for UI elements. 
- **SQLite / SQL Schema**: For data storage and testing. 

## Browser Compatibility

The application works with all modern browsers that support HTML5 and CSS3, including:

- Chrome 90+
- Firefox 88+ 
- Safari 14+ 
- Edge 90+

**Note:** This is a static HTML/CSS application. For production use, backend functionality would be required for database connectivity and form processing. 
