<div align="center">

# 🚆 AAGAMI RAIL

### Intelligent Railway Traffic Management & Disaster Response

**Smarter scheduling. Faster decisions. Resilient railway networks.**

An AI-powered railway traffic management prototype developed for **Smart India Hackathon 2025**, focused on train scheduling optimization, conflict resolution, disaster simulation, and intelligent route planning.

<br/>

![Project](https://img.shields.io/badge/Project-AAGAMI%20RAIL-2563EB?style=for-the-badge)
![SIH](https://img.shields.io/badge/Smart%20India%20Hackathon-2025-F97316?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-FastAPI-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Database](https://img.shields.io/badge/Database-MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)

<br/>

**Designed to help railway traffic controllers make better-informed operational decisions.**

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [The Problem](#-the-problem)
- [Our Solution](#-our-solution)
- [Key Features](#-key-features)
- [How It Works](#-how-it-works)
- [Technology Stack](#-technology-stack)
- [System Architecture](#-system-architecture)
- [Optimization Algorithms](#-optimization-algorithms)
- [Disaster Management](#-disaster-management)
- [API Overview](#-api-overview)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [Future Scope](#-future-scope)
- [Important Disclaimer](#-important-disclaimer)
- [Acknowledgements](#-acknowledgements)

---

## 🚀 Overview

Railway networks are complex systems where multiple trains, shared tracks, station schedules, and unexpected disruptions must be managed together.

**AAGAMI RAIL** explores how intelligent algorithms and interactive visualization can assist railway traffic management by identifying scheduling conflicts, optimizing train priorities, simulating disruptions, and finding alternative routes.

The platform combines a React-based interface, a FastAPI backend, and MongoDB to create a centralized environment for railway network monitoring and decision support.

### What makes AAGAMI RAIL different?

- 🧠 **Intelligent scheduling:** Analyze conflicts and prioritize trains.
- 🛤️ **Route optimization:** Explore alternative paths when routes become unavailable.
- 🌧️ **Disaster simulation:** Evaluate the effects of railway disruptions.
- 📊 **Operational analytics:** Visualize delays, train status, and performance indicators.
- 🗺️ **Interactive network visualization:** Understand railway topology and route conditions through a visual interface.
- 🔎 **Decision transparency:** Compare original and optimized schedules to understand proposed changes.

> **Our vision:** Make railway traffic management more intelligent, visual, and responsive through software-assisted decision-making.

---

## 🎯 The Problem

Railway traffic management involves coordinating train movements across interconnected tracks and stations while responding to changing operational conditions.

Several challenges make this difficult:

| Challenge | Why It Matters |
|---|---|
| Scheduling conflicts | Multiple trains may require the same route section during overlapping time windows. |
| Traffic congestion | Poor scheduling decisions can contribute to delays and inefficient track utilization. |
| Unexpected disruptions | Flooding, equipment failures, weather, and breakdowns can affect planned operations. |
| Alternative routing | Controllers need to evaluate available paths when a route becomes unavailable. |
| Limited network visibility | Understanding the combined effects of disruptions across a network can be difficult. |
| Decision complexity | Operational changes must account for priorities, delays, and route availability. |

### The opportunity

AAGAMI RAIL investigates how algorithmic scheduling, route-search techniques, disruption simulation, and a unified visual dashboard can support these decisions.

---

## 💡 Our Solution

AAGAMI RAIL brings railway scheduling, route analysis, disruption management, and operational visualization into one prototype.

### 01 — Analyze

Represent trains, stations, routes, schedules, and route conditions in a connected network.

### 02 — Detect

Identify potential scheduling conflicts and determine which trains or route sections may be affected.

### 03 — Optimize

Apply priority-based scheduling and delay-minimization heuristics to explore improved train schedules.

### 04 — Respond

Simulate railway disruptions and search for alternative paths around blocked route sections.

### 05 — Visualize

Present network conditions, train information, alerts, and before-and-after optimization results through the dashboard.

---

## ✨ Key Features

### 🧠 1. Intelligent Train Scheduling

The scheduling module explores ways to resolve conflicts and improve train movement through priority-based decision-making.

- Detect overlapping scheduled time windows on shared route sections.
- Assign priority weights to trains.
- Apply scheduling adjustments to resolve modeled conflicts.
- Explore delay-minimization strategies.
- Compare original and optimized schedules.
- Explain proposed changes through a decision summary.

**Priority model described in the project report:**

| Priority | Weight |
|---|---:|
| High | 3 |
| Medium | 2 |
| Low | 1 |

These weights represent the prototype's scheduling model and are not a substitute for official railway operating rules.

### 🌧️ 2. Disaster Management

Simulate disruptions that may affect railway operations and evaluate their potential consequences.

Supported scenarios described in the project report include:

- 🌊 Track flooding
- ⚙️ Equipment or signal failure
- 🌫️ Weather-related disruption
- 🚧 Train breakdown
- ⛔ Track blockade or strike
- 🚑 Emergency train insertion

The prototype can model affected route sections, estimate disruption impacts, and attempt alternative-route planning.

### 🗺️ 3. Interactive Railway Network

Explore the railway network through a visual representation of stations, routes, and train movement.

- SVG-based railway network visualization.
- Station and route representations.
- Animated train markers.
- Train information views.
- Blocked-route indicators.
- Speed-restricted route indicators.
- Highlighted alternative paths.

The visualization is intended to make network conditions easier to understand than a schedule presented only as text.

### 📊 4. Performance Analytics

Bring important operational indicators into one dashboard.

The project report describes metrics such as:

- Total trains represented in the system.
- Average train delay.
- On-time performance.
- Route and section utilization indicators.
- Rerouted-train statistics.
- Disruption impact summaries.
- Optimization recommendations.

The values displayed depend on the network data and calculations implemented by the application.

### 🔍 5. Optimization Explanations

Scheduling changes should be understandable, not just displayed as new numbers.

The project includes a **"What Changed?"** concept for comparing original and optimized schedules and presenting explanations of proposed decisions.

This helps users examine why a train's timing or route may have changed.

---

## ⚙️ How It Works

The application follows a straightforward data-processing workflow.

```text
                ┌────────────────────────┐
                │   User / Controller    │
                └────────────┬───────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │    React Frontend      │
                │  Dashboard & Network   │
                └────────────┬───────────┘
                             │
                         HTTP / JSON
                             │
                             ▼
                ┌────────────────────────┐
                │    FastAPI Backend     │
                │                        │
                │  Conflict Detection    │
                │  Schedule Optimization │
                │  Disaster Simulation   │
                │  Route Search          │
                └────────────┬───────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │       MongoDB          │
                │                        │
                │  Trains & Stations     │
                │  Routes & Disruptions  │
                │  Optimization Records  │
                └────────────────────────┘
```

### Example workflow

1. The frontend requests railway network information.
2. The backend retrieves the required data.
3. A scheduling or disruption operation is submitted.
4. The backend applies the relevant algorithm to the modeled network.
5. The application returns the resulting schedule, route information, or analysis.
6. The dashboard presents the results for inspection.

---

## 🛠️ Technology Stack

AAGAMI RAIL combines a modern web interface with a Python-based backend and a document-oriented database.

<table>
<tr>
<td width="50%" valign="top">

### 🎨 Frontend

- **React 18** — User interface
- **JavaScript** — Application logic
- **React Router DOM** — Client-side routing
- **Tailwind CSS** — Styling
- **shadcn/ui** — Interface components
- **Lucide React** — Icons
- **Axios** — HTTP requests
- **SVG** — Network visualization

</td>
<td width="50%" valign="top">

### ⚡ Backend

- **Python 3.9+** — Backend language
- **FastAPI** — API framework
- **Uvicorn** — ASGI server
- **Pydantic** — Data validation
- **Motor** — Asynchronous MongoDB driver
- **JWT** — Authentication approach described in the report

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 🗄️ Database

- **MongoDB**
- Train records
- Station information
- Route topology
- Disruption records
- Optimization results
- Alerts and notifications

</td>
<td width="50%" valign="top">

### 🔧 Development & Deployment

- Git and GitHub
- Yarn and npm-compatible frontend tooling
- pip for Python dependencies
- Docker support described in the project report
- OpenAPI documentation through FastAPI

</td>
</tr>
</table>

---

## 🏗️ System Architecture

The project is organized around three primary layers.

| Layer | Responsibility |
|---|---|
| Presentation layer | Displays the railway network, train information, alerts, and optimization results. |
| Application layer | Processes requests, detects conflicts, runs scheduling logic, and evaluates disruptions. |
| Data layer | Stores and retrieves train, station, route, and related operational records. |

### Data flow

```text
Frontend
   │
   ▼
API Request
   │
   ▼
Backend Validation
   │
   ▼
Scheduling / Route Search / Disaster Analysis
   │
   ▼
Database Operations, Where Required
   │
   ▼
API Response
   │
   ▼
Updated Dashboard and Network Visualization
```

---

## 🧮 Optimization Algorithms

The project report describes a combination of graph-search, scheduling, and heuristic techniques.

| Technique | Purpose |
|---|---|
| Interval intersection | Detect overlapping scheduled time windows. |
| Weighted priority scheduling | Represent train priority during conflict resolution. |
| Breadth-First Search (BFS) | Search a modeled network for alternative routes. |
| Greedy scheduling heuristics | Explore feasible scheduling adjustments and delay reduction. |
| Disruption impact estimation | Estimate the potential effects of a modeled incident. |

### Alternative-route search

The railway network can be represented as a graph:

- **Nodes:** Stations.
- **Edges:** Connections between stations.
- **Blocked edges:** Route segments unavailable in a simulated disruption.
- **Alternative path:** A path that avoids the modeled blocked segments.

The route-search process can be represented as:

```text
Input:
    Starting station
    Destination station
    Railway network
    Blocked route segments

Process:
    Exclude unavailable route segments
    Search the remaining network using BFS
    Evaluate candidate paths within the model's constraints

Output:
    Candidate alternative path, if one is found
```

The algorithms operate on the network and constraints represented in the prototype. They do not establish that a route is safe or authorized for real railway operations.

---

## 🌧️ Disaster Management in Action

AAGAMI RAIL explores how railway network conditions might change when an incident occurs.

### Example: Simulated route flooding

Suppose a route segment between stations A and B becomes unavailable.

**Before the disruption:**

```text
Station A ───────── Station B
           Available
```

**During the disruption:**

```text
Station A ──── X ─── Station B
             Blocked
```

**Possible alternative route:**

```text
              Station C
             /         \
            /           \
      Station A       Station B
```

The application can search for an alternative path through the modeled network and evaluate the resulting route and schedule changes.

This is an illustrative example, not a live railway route or an operational rerouting recommendation.

---

## 🔌 API Overview

The project report documents the following API endpoints.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/trains` | Retrieve train information. |
| `GET` | `/api/stations` | Retrieve station information. |
| `GET` | `/api/routes` | Retrieve route topology and status. |
| `POST` | `/api/optimize` | Run schedule optimization. |
| `POST` | `/api/disaster` | Apply a disaster scenario. |
| `POST` | `/api/disaster/custom` | Submit a custom disruption scenario. |
| `GET` | `/api/system/status` | Retrieve system status information. |

> **Note:** These endpoints are documented in the project report. Confirm their current implementation, request schemas, and response formats against the repository's backend code.

FastAPI commonly provides interactive API documentation at `/docs` when enabled by the application.

---

## 🚀 Getting Started

To run AAGAMI RAIL locally, you will need:

- Git
- Node.js and a compatible package manager
- Python 3.9 or newer
- MongoDB
- The project's frontend and backend dependencies

### 1. Clone the repository

```bash
git clone https://github.com/aagami-rail/prototype.git
cd prototype
```

### 2. Inspect the project structure

Before installing dependencies, identify the frontend and backend directories.

```bash
ls
```

On Windows Command Prompt, you can use:

```bat
dir
```

### 3. Start the backend

Navigate to the directory containing the backend's Python dependency file and application entry point.

Create and activate a virtual environment if the project supports this workflow:

```bash
python -m venv .venv
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

Install the dependencies using the repository's actual dependency file.

For example, if the backend contains `requirements.txt`:

```bash
pip install -r requirements.txt
```

Start the FastAPI application using its actual module path. For example, if the entry point is `main.py` and defines `app`:

```bash
uvicorn main:app --reload --port 8001
```

### 4. Start the frontend

Open a second terminal and navigate to the directory containing the frontend's `package.json`.

Install the dependencies:

```bash
npm install
```

Start the application using the script defined in `package.json`. For example:

```bash
npm start
```

### 5. Configure the database and API connection

Make sure MongoDB is running and the backend is configured to connect to it.

Configure the frontend's API base URL to point to the backend.

**Important:** The commands above are examples. The repository's actual folder structure, dependency files, entry points, environment variables, and package scripts determine the exact startup commands.

---

## 📁 Project Structure

The project report describes a React frontend and a Python FastAPI backend.

A possible high-level organization is:

```text
AAGAMI-RAIL/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── ...
│
├── README.md
└── .gitignore
```

This is an illustrative layout, **not a verified listing of the current repository files**. Adjust it to match the actual codebase.

---

## 🧪 Testing

The project report records **17 out of 17 test scenarios passed** for its reported testing environment, including scenarios involving core API functionality, scheduling, disaster simulation, and frontend-backend communication.

These are results reported by the project team, not an independently reproduced test result.

For future development, recommended validation areas include:

- Scheduling conflict detection.
- Priority-based schedule changes.
- Alternative-route search.
- Blocked-route handling.
- Invalid API requests.
- Database connectivity and error handling.
- Frontend-backend integration.
- Large network and concurrent-request behavior.

Test commands should be added here once the actual repository's testing framework and scripts have been verified.

---

## 🔭 Future Scope

Potential directions for further development include:

- **Live train data integration:** Connect validated operational data sources.
- **Predictive analytics:** Explore models for delay and disruption estimation.
- **Weather integration:** Incorporate external weather data where available.
- **Advanced optimization:** Evaluate more sophisticated scheduling and route-planning algorithms.
- **Network-scale simulation:** Test larger railway graphs and more complex scenarios.
- **Historical analytics:** Compare performance across stored simulation runs.
- **Improved explainability:** Provide clearer explanations of proposed scheduling decisions.
- **Deployment improvements:** Add reproducible environment configuration, monitoring, and automated testing.
- **Safety validation:** Establish formal requirements and independent evaluation before any real-world operational use.

These are development opportunities rather than claims that the capabilities are already implemented.

---

## ⚠️ Important Disclaimer

AAGAMI RAIL is a **prototype for railway traffic optimization research, simulation, and decision-support exploration**.

It is not certified railway signalling software and must not be used to control real trains, authorize routes, override railway operating rules, or make safety-critical operational decisions.

Any future real-world application would require validated data, railway-domain expertise, formal safety engineering, independent verification, regulatory approval, and authorized human oversight.

---

## 🏆 Acknowledgements

Developed in the context of **Smart India Hackathon 2025**, under the theme of transportation and logistics.

The project explores the use of software engineering, graph algorithms, scheduling techniques, and interactive visualization to investigate challenges in railway traffic management.

---

<div align="center">

## 🚆 AAGAMI RAIL

**Intelligence for a more connected railway network.**

*Explore. Optimize. Respond.*

</div>
