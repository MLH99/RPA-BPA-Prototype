# BPA / RPA Demo Environment

This repository contains a small demo setup that simulates a real-life
utility workflow:

**LIME (CRM) → Elsmart (web) → BFUS (service & agreements)**

The purpose of this project is to demonstrate the difference between:

-   Classic **RPA** (UI automation, image matching, mouse clicks)
-   Modern **BPA** (API-driven process automation)

Everything is simulated. No real systems are connected.

------------------------------------------------------------------------

## Project Overview

### lime_crm_clone_v2.py

Desktop CRM-style interface.

Includes: - Case overview - Tjänstenummer - Kundnummer - Checklist -
Action buttons

This is the starting point of the process.

------------------------------------------------------------------------

### index.html + styles.css

Static Elsmart web clone.

Contains example values such as: - Ref. nr. - Anläggnings-id -
Mätarnr. - Kommun - Installatör - Fastighetsägare

Used by: - Selenium (RPA robot) - BPA demo engine

------------------------------------------------------------------------

### bfus_clone_v3.py

Desktop clone of BFUS.

Includes: - Overgripande uppgifter - Search popup (Sök tjänst) -
Agreement wizard (Skapa avtal) - Price parameters - Fakturavillkor -
Visual update markers

This is where service data is updated and agreements are created.

------------------------------------------------------------------------

### bpa_demo_v2.py

API-driven automation demo.

Opens: - LIME window - BFUS window - Elsmart data window - Control panel

Allows: - Running full process - Running step-by-step - Resetting state

No image recognition is used here. The automation calls simulated system
APIs directly.

------------------------------------------------------------------------

### rpa_robot_with_start_button_v2.py

Human-style RPA robot.

Uses: - PyAutoGUI - OpenCV template matching - Selenium (for Elsmart)

The robot: - Clicks based on screenshots - Types like a human - Waits
for popups - Switches windows - Extracts web data - Fills BFUS forms

This version is intentionally more fragile --- it shows how traditional
RPA behaves.

------------------------------------------------------------------------

## Process Flow

1.  Open LIME case
2.  Read data
3.  Open Elsmart
4.  Extract:
    -   Anläggnings-id
    -   Ref nr
    -   Mätarnr
    -   Säkring
5.  Switch to BFUS
6.  Update service
7.  Create agreement
8.  Save agreement
9.  Return to LIME
10. Update checklist

------------------------------------------------------------------------

## How to Run

### Run BPA demo (recommended)

python bpa_demo_v2.py

Then use: - "Kör hela processen" or - "Kör steg för steg"

------------------------------------------------------------------------

### Run RPA robot

1.  Start local web server in folder with index.html:

python -m http.server 8000

2.  Run robot:

python rpa_robot_with_start_button_v2.py --run

Make sure: - Template PNG files exist in /templates - Windows are
visible - Screen resolution matches template images

------------------------------------------------------------------------

## Folder Structure

. ├── bpa_demo_v2.py ├── bfus_clone_v3.py ├── lime_crm_clone_v2.py ├──
rpa_robot_with_start_button_v2.py ├── index.html ├── styles.css └──
templates/

------------------------------------------------------------------------

## Notes

-   All systems are simulated.
-   No real integrations.
-   Generic demo data.
-   Built for automation discussions, demos, and workshops.
