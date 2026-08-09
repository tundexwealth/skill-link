import csv
import os
import re
import sys
from pathlib import Path
from typing import Optional

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from models import Category, Location, Provider, Service
from db.base import Base
from db.session import SessionLocal, engine
from db.migrations import ensure_schema

categories = [
    {
        "name": "Cleaning",
        "description": "Professional home and office cleaning services for every space.",
        "image_url": "assets/img/gallery/location3.png",
    },
    {
        "name": "Plumbing",
        "description": "Expert plumbing repairs, installations, and maintenance for homes.",
        "image_url": "assets/img/gallery/location1.png",
    },
    {
        "name": "Electrical",
        "description": "Reliable electrical installations, repairs, and wiring solutions.",
        "image_url": "assets/img/gallery/location2.png",
    },
    {
        "name": "Generator Repair",
        "description": "Generator servicing, troubleshooting, and repair by skilled technicians.",
        "image_url": "assets/img/gallery/generator_repair.jpg",
    },
    {
        "name": "Phone Repair",
        "description": "Fast smartphone repairs including screens, batteries, and software fixes.",
        "image_url": "assets/img/gallery/phone_repair.jpg",
    },
    {
        "name": "Computer Repair",
        "description": "Laptop and desktop repair, upgrades, and maintenance services.",
        "image_url": "assets/img/gallery/computer_repair.jpg",
    },
    {
        "name": "Tutoring",
        "description": "Experienced tutors helping students excel in various academic subjects.",
        "image_url": "assets/img/gallery/location4.png",
    },
    {
        "name": "Laundry",
        "description": "Convenient washing, drying, ironing, and garment care services.",
        "image_url": "assets/img/gallery/laundry.jpg",
    },
    {
        "name": "Moving Services",
        "description": "Safe and efficient residential and commercial relocation assistance.",
        "image_url": "assets/img/gallery/moving_services.jpg",
    },
    {
        "name": "Home Painting",
        "description": "Interior and exterior painting with quality finishes and materials.",
        "image_url": "assets/img/gallery/home_painting.jpg",
    },
    {
        "name": "Car Repair",
        "description": "Professional vehicle diagnostics, repairs, and regular maintenance services.",
        "image_url": "assets/img/gallery/car_repair.jpg",
    },
    {
        "name": "Photography",
        "description": "Capture memorable moments with professional photography services.",
        "image_url": "assets/img/gallery/photography.jpg",
    },
    {
        "name": "Catering",
        "description": "Delicious catering services for weddings, parties, and corporate events.",
        "image_url": "assets/img/gallery/catering.jpg",
    },
    {
        "name": "Event Planning",
        "description": "Complete event planning and coordination for memorable occasions.",
        "image_url": "assets/img/gallery/event_planning.jpg",
    },
    {
        "name": "Hair Styling",
        "description": "Modern haircuts, styling, treatments, and salon beauty services.",
        "image_url": "assets/img/gallery/hair_styling.jpg",
    },
    {
        "name": "Makeup Artist",
        "description": "Professional makeup services for weddings, parties, and photoshoots.",
        "image_url": "assets/img/gallery/makeup_artist.jpg",
    },
    {
        "name": "Interior Design",
        "description": "Creative interior designs that transform homes and commercial spaces.",
        "image_url": "assets/img/gallery/interior_design.jpg",
    },
    {
        "name": "Security Services",
        "description": "Reliable security personnel for homes, businesses, and special events.",
        "image_url": "assets/img/gallery/security_services.jpg",
    },
    {
        "name": "Air Conditioner Repair",
        "description": "Air conditioning installation, servicing, and repair by certified experts.",
        "image_url": "assets/img/gallery/air_conditioner_repair.jpg",
    },
    {
        "name": "Furniture Repair",
        "description": "Restore damaged furniture with expert repair and refinishing services.",
        "image_url": "assets/img/gallery/furniture_repair.jpg",
    },
]

locations = [
    {
        "area": "Ita-Ale",
        "city": "Ijebu-Ode",
        "state": "Ogun",
        "address": "No 5, Ita-Ale Road, opposite Central Mosque, Ita-Ale, Ijebu-Ode",
    },
    {
        "area": "Igbeba",
        "city": "Ijebu-Ode",
        "state": "Ogun",
        "address": "No 10, ABC Road, opposite First Bank, Igbeba, Ijebu-Ode",
    },
    {
        "area": "Molipa",
        "city": "Ijebu-Ode",
        "state": "Ogun",
        "address": "No 8, Molipa Street, near Oba's Palace, Molipa, Ijebu-Ode",
    },
    {
        "area": "Oke-Aje",
        "city": "Ijebu-Ode",
        "state": "Ogun",
        "address": "No 15, Oke-Aje Avenue, close to Main Market, Oke-Aje, Ijebu-Ode",
    },
    {
        "area": "Oke-Owa",
        "city": "Ijebu-Ode",
        "state": "Ogun",
        "address": "No 20, Oke-Owa Lane, beside Community Center, Oke-Owa, Ijebu-Ode",
    },
    {
        "area": "Odo-Esa",
        "city": "Ijebu-Ode",
        "state": "Ogun",
        "address": "No 12, Odo-Esa Plaza, near GSM Market, Odo-Esa, Ijebu-Ode",
    },
    {
        "area": "Imowo",
        "city": "Ijebu-Ode",
        "state": "Ogun",
        "address": "No 7, Imowo Estate, close to Primary School, Imowo, Ijebu-Ode",
    },
    {
        "area": "Ayetoro",
        "city": "Ijebu-Ode",
        "state": "Ogun",
        "address": "No 18, Ayetoro Road, opposite Police Station, Ayetoro, Ijebu-Ode",
    },
    {
        "area": "Itantebo",
        "city": "Ijebu-Ode",
        "state": "Ogun",
        "address": "No 9, Itantebo Junction, near Gas Station, Itantebo, Ijebu-Ode",
    },
    {
        "area": "Porogun",
        "city": "Ijebu-Ode",
        "state": "Ogun",
        "address": "No 25, Porogun Street, beside Health Center, Porogun, Ijebu-Ode",
    },
    {
        "area": "Ijasi",
        "city": "Ijebu-Ode",
        "state": "Ogun",
        "address": "No 3, Ijasi Road, opposite School, Ijasi, Ijebu-Ode",
    },
    {
        "area": "Awa",
        "city": "Ijebu-Ode",
        "state": "Ogun",
        "address": "No 14, Awa Avenue, near Market, Awa, Ijebu-Ode",
    },
    {
        "area": "Isiwo",
        "city": "Ijebu-Ode",
        "state": "Ogun",
        "address": "No 22, Isiwo Lane, close to Bank, Isiwo, Ijebu-Ode",
    },
    {
        "area": "Ago-Iwoye",
        "city": "Ago-Iwoye",
        "state": "Ogun",
        "address": "No 11, Ago-Iwoye Road, opposite Town Hall, Ago-Iwoye",
    },
    {
        "area": "Ijebu-Igbo",
        "city": "Ijebu-Igbo",
        "state": "Ogun",
        "address": "No 6, Ijebu-Igbo Street, near Market Square, Ijebu-Igbo",
    },
    {
        "area": "Isonyin",
        "city": "Isonyin",
        "state": "Ogun",
        "address": "No 13, Isonyin Avenue, opposite Church, Isonyin",
    },
    {
        "area": "Ijebu-Imusin",
        "city": "Ijebu-Imusin",
        "state": "Ogun",
        "address": "No 19, Ijebu-Imusin Road, near Community Hall, Ijebu-Imusin",
    },
    {
        "area": "Oru",
        "city": "Oru",
        "state": "Ogun",
        "address": "No 4, Oru Lane, beside Market, Oru",
    },
    {
        "area": "Imagbon",
        "city": "Imagbon",
        "state": "Ogun",
        "address": "No 17, Imagbon Street, close to School, Imagbon",
    },
    {
        "area": "Ilaporu",
        "city": "Ijebu-Ode",
        "state": "Ogun",
        "address": "No 23, Ilaporu Road, opposite Clinic, Ilaporu, Ijebu-Ode",
    },
]

providers = [
    {"business_name": "Bright Cleaning Services", "phone": "08030000001"},
    {"business_name": "Adebayo Electricals", "phone": "08030000002"},
    {"business_name": "OgunTech Repairs", "phone": "08030000003"},
    {"business_name": "Swift Plumbing Works", "phone": "08030000004"},
    {"business_name": "Spark Laundry Hub", "phone": "08030000005"},
    {"business_name": "Prime Tutors Academy", "phone": "08030000006"},
    {"business_name": "Elite Event Planners", "phone": "08030000007"},
    {"business_name": "Golden Caterers", "phone": "08030000008"},
    {"business_name": "Vision Photography", "phone": "08030000009"},
    {"business_name": "Beauty Touch Studio", "phone": "08030000010"},
    {"business_name": "Hair Palace", "phone": "08030000011"},
    {"business_name": "SecureHome Systems", "phone": "08030000012"},
    {"business_name": "CoolAir Solutions", "phone": "08030000013"},
    {"business_name": "QuickFix Furniture", "phone": "08030000014"},
    {"business_name": "Master Painters", "phone": "08030000015"},
    {"business_name": "MoveEasy Logistics", "phone": "08030000016"},
    {"business_name": "AutoCare Garage", "phone": "08030000017"},
    {"business_name": "Mobile Doctor Repairs", "phone": "08030000018"},
    {"business_name": "Laptop Rescue Center", "phone": "08030000019"},
    {"business_name": "PowerGen Experts", "phone": "08030000020"},
    {"business_name": "Stylish Spaces Interiors", "phone": "08030000021"},
]


SERVICE_IMAGE_MAP = {
    "Cleaning": "assets/img/gallery/location3.png",
    "Plumbing": "assets/img/gallery/location1.png",
    "Electrical": "assets/img/gallery/location2.png",
    "Generator Repair": "assets/img/gallery/generator_repair.jpg",
    "Phone Repair": "assets/img/gallery/phone_repair.jpg",
    "Computer Repair": "assets/img/gallery/computer_repair.jpg",
    "Tutoring": "assets/img/gallery/location4.png",
    "Laundry": "assets/img/gallery/laundry.jpg",
    "Moving Services": "assets/img/gallery/moving_services.jpg",
    "Home Painting": "assets/img/gallery/home_painting.jpg",
    "Car Repair": "assets/img/gallery/car_repair.jpg",
    "Photography": "assets/img/gallery/photography.jpg",
    "Catering": "assets/img/gallery/catering.jpg",
    "Event Planning": "assets/img/gallery/event_planning.jpg",
    "Hair Styling": "assets/img/gallery/hair_styling.jpg",
    "Makeup Artist": "assets/img/gallery/makeup_artist.jpg",
    "Interior Design": "assets/img/gallery/interior_design.jpg",
    "Security Services": "assets/img/gallery/security_services.jpg",
    "Air Conditioner Repair": "assets/img/gallery/air_conditioner_repair.jpg",
    "Furniture Repair": "assets/img/gallery/furniture_repair.jpg",
}


def build_services():
    category_service_templates = {
        "Cleaning": [
            (
                "Deep Home Cleaning",
                "A detailed deep-cleaning package for kitchens, bathrooms, bedrooms, and living areas using safe and effective products.",
                "15000",
            ),
            (
                "Office Sanitizing",
                "Reliable sanitizing and dusting for shared workspaces, desks, and meeting rooms to keep your team comfortable.",
                "25000",
            ),
            (
                "Move-In Cleaning",
                "A fresh-start cleaning service for new homes, covering floors, surfaces, cabinets, and hidden corners.",
                "28000",
            ),
            (
                "Post-Construction Cleanup",
                "Thorough cleanup after renovations, removing dust, debris, and paint residue with professional care.",
                "32000",
            ),
            (
                "Carpet and Sofa Cleaning",
                "Deep treatment for upholstery and carpets that lifts stains, odors, and everyday grime.",
                "22000",
            ),
            (
                "Window Cleaning",
                "Spotless interior and exterior window cleaning for homes, shops, and offices.",
                "18000",
            ),
            (
                "Kitchen Deep Clean",
                "Focused kitchen cleaning for cabinets, appliances, sinks, and backsplash areas.",
                "20000",
            ),
            (
                "Bathroom Sanitizing",
                "Hygienic bathroom cleaning that tackles tiles, fixtures, mirrors, and drains with precision.",
                "17000",
            ),
            (
                "Commercial Cleaning",
                "Scheduled cleaning support for retail spaces, clinics, and small businesses.",
                "30000",
            ),
            (
                "Eco-Friendly Cleaning",
                "Green cleaning service using low-toxicity products for homes that need a gentler touch.",
                "24000",
            ),
        ],
        "Plumbing": [
            (
                "Residential Pipe Repair",
                "Fast repair of leaking or burst pipes to protect your property and restore water flow quickly.",
                "18000",
            ),
            (
                "Drain Unclogging",
                "Effective clearing of blocked sinks, showers, and drains with minimal disruption to your routine.",
                "12000",
            ),
            (
                "Water Heater Installation",
                "Professional installation of water heaters with safe connections and lasting performance.",
                "35000",
            ),
            (
                "Toilet Fixing",
                "Reliable repairs for running toilets, faulty mechanisms, and weak flushing systems.",
                "15000",
            ),
            (
                "Bathroom Plumbing",
                "Complete plumbing support for taps, shower heads, and bathroom fixtures with neat workmanship.",
                "22000",
            ),
            (
                "Kitchen Plumbing",
                "Installation and upkeep for kitchen sinks, garbage disposals, and supply lines.",
                "24000",
            ),
            (
                "Leak Detection",
                "Careful inspection and diagnosis of hidden leaks before they cause lasting property damage.",
                "16000",
            ),
            (
                "Pipe Replacement",
                "Upgrade old or worn piping with durable solutions designed for long-term reliability.",
                "28000",
            ),
            (
                "Emergency Plumbing",
                "Rapid response for urgent plumbing issues that need practical fixes on short notice.",
                "20000",
            ),
            (
                "Water Pressure Repair",
                "Restoration of steady water pressure for better comfort and consistent daily use.",
                "19000",
            ),
        ],
        "Electrical": [
            (
                "House Rewiring",
                "Full electrical rewiring for older homes, improving safety, efficiency, and long-term reliability.",
                "50000",
            ),
            (
                "Ceiling Fan Installation",
                "Neat installation of ceiling fans for improved airflow and better room comfort.",
                "14000",
            ),
            (
                "Socket and Switch Repair",
                "Quick fixes for loose outlets, faulty switches, and aging electrical points.",
                "12000",
            ),
            (
                "Lighting Upgrade",
                "Modern lighting installations for brighter, more stylish interiors and workspaces.",
                "18000",
            ),
            (
                "Outdoor Wiring",
                "Safe wiring solutions for gates, compound lighting, and exterior power needs.",
                "26000",
            ),
            (
                "Power Surge Protection",
                "Installation of protection systems that help guard sensitive appliances against voltage issues.",
                "22000",
            ),
            (
                "Generator Connection",
                "Professional connection setup for generators with proper safety checks and stable performance.",
                "32000",
            ),
            (
                "Electrical Inspection",
                "Detailed inspection services that help identify faults before they become expensive repairs.",
                "16000",
            ),
            (
                "New Circuit Installation",
                "Custom installation for additional power points and dedicated circuits in busy homes.",
                "30000",
            ),
            (
                "Emergency Electrical Fix",
                "Prompt troubleshooting for power failures, sparks, and urgent electrical concerns.",
                "21000",
            ),
        ],
        "Generator Repair": [
            (
                "Generator Maintenance",
                "Routine servicing that keeps generators running smoothly and reduces the risk of sudden failure.",
                "20000",
            ),
            (
                "Fuel System Service",
                "Inspection and cleaning of fuel components to improve efficiency and steady operation.",
                "17000",
            ),
            (
                "Battery Replacement",
                "Fresh battery installation to restore dependable starting power and reliable performance.",
                "14000",
            ),
            (
                "Startup Troubleshooting",
                "Diagnosis of startup issues so your generator can come alive when you need it most.",
                "16000",
            ),
            (
                "Cooling System Repair",
                "Repair of overheating issues to protect the engine and extend generator life.",
                "19000",
            ),
            (
                "Alternator Repair",
                "Skilled alternator servicing to maintain steady electrical output and power stability.",
                "24000",
            ),
            (
                "Commercial Generator Service",
                "Maintenance support for businesses with regular power needs and high reliability expectations.",
                "30000",
            ),
            (
                "Transfer Switch Setup",
                "Professional integration of generator switches for safe and smooth power changes.",
                "28000",
            ),
            (
                "Generator Tune-Up",
                "Comprehensive tune-up service that improves performance, fuel efficiency, and durability.",
                "23000",
            ),
            (
                "Emergency Generator Repair",
                "Fast-response repair service for sudden breakdowns and urgent power restoration needs.",
                "26000",
            ),
        ],
        "Phone Repair": [
            (
                "Android Phone Repair",
                "Screen, battery, and hardware repairs tailored to common smartphone issues and everyday usage.",
                "10000",
            ),
            (
                "iPhone Screen Fix",
                "Professional screen replacement and display repair for cracked or unresponsive devices.",
                "15000",
            ),
            (
                "Battery Replacement",
                "Long-lasting battery upgrades that improve phone performance and daily reliability.",
                "8000",
            ),
            (
                "Charging Port Repair",
                "Repair of damaged charging ports to restore fast and consistent charging.",
                "9000",
            ),
            (
                "Water Damage Recovery",
                "Careful cleaning and restoration for phones affected by liquid damage.",
                "12000",
            ),
            (
                "Software Troubleshooting",
                "Diagnosis and repair of app glitches, boot problems, and system slowdowns.",
                "7000",
            ),
            (
                "Camera Module Repair",
                "Fixes for blurry cameras, shutter issues, and damaged rear camera units.",
                "11000",
            ),
            (
                "Phone Data Transfer",
                "Safe transfer of contacts, media, and files to a new device with minimal effort.",
                "6000",
            ),
            (
                "Phone Unlocking",
                "Trusted unlocking service for supported devices with simple and secure procedures.",
                "10000",
            ),
            (
                "Screen Protector Installation",
                "Professional installation of protective glass to keep phones safe from everyday wear.",
                "5000",
            ),
        ],
        "Computer Repair": [
            (
                "Laptop Repair",
                "Hardware and software troubleshooting for slow, damaged, or unstable laptops.",
                "12000",
            ),
            (
                "Desktop Maintenance",
                "Routine servicing for desktops that improves performance, cooling, and reliability.",
                "14000",
            ),
            (
                "Virus Removal",
                "Careful malware cleanup and security checks to help restore safe computer use.",
                "10000",
            ),
            (
                "SSD Upgrade",
                "Fast storage upgrade service that boosts speed, responsiveness, and file access.",
                "18000",
            ),
            (
                "Keyboard Replacement",
                "Replacement of worn or broken keyboards for smooth typing and better comfort.",
                "8000",
            ),
            (
                "Screen Replacement",
                "Professional screen repair for laptops and monitors with clear, dependable results.",
                "16000",
            ),
            (
                "Data Recovery",
                "Careful recovery support for inaccessible files and important system data.",
                "22000",
            ),
            (
                "Printer Setup",
                "Installation and troubleshooting for printers and home office networking needs.",
                "9000",
            ),
            (
                "Software Installation",
                "Setup of essential software and drivers tailored to your work and learning needs.",
                "7000",
            ),
            (
                "Laptop Cooling Service",
                "Cleaning and maintenance that prevents overheating and helps extend device life.",
                "10000",
            ),
        ],
        "Tutoring": [
            (
                "Mathematics Home Tutor",
                "Patient one-on-one help for secondary school students who need clearer explanations and steady practice.",
                "25000",
            ),
            (
                "English Language Tutor",
                "Support for grammar, comprehension, essay writing, and spoken communication skills.",
                "22000",
            ),
            (
                "Science Revision Class",
                "Focused lessons in biology, chemistry, and physics that make complex topics easier to grasp.",
                "24000",
            ),
            (
                "Exam Prep Coaching",
                "Targeted preparation for school exams with practical study strategies and review sessions.",
                "26000",
            ),
            (
                "Junior Secondary Tutor",
                "Structured tutoring for younger learners building confidence in core school subjects.",
                "20000",
            ),
            (
                "Online Homework Support",
                "Flexible online guidance for assignments, projects, and revision planning.",
                "18000",
            ),
            (
                "Reading Improvement",
                "Skill-building sessions that improve reading speed, comprehension, and confidence.",
                "19000",
            ),
            (
                "Essay Writing Coach",
                "Step-by-step support for writing clear, organized, and well-structured essays.",
                "21000",
            ),
            (
                "Study Skills Coaching",
                "Practical lessons that help students manage time, stay organized, and study effectively.",
                "17000",
            ),
            (
                "Primary School Tutor",
                "Friendly tutoring for foundational subjects with patient explanations and steady encouragement.",
                "16000",
            ),
        ],
        "Laundry": [
            (
                "Laundry Pickup Service",
                "Convenient pickup and delivery for clothes, bedsheets, and daily laundry needs.",
                "5000",
            ),
            (
                "Wash and Iron",
                "Careful washing and ironing for shirts, uniforms, and household clothing.",
                "4000",
            ),
            (
                "Dry Cleaning",
                "Professional cleaning for delicate clothes that need extra care and finishing.",
                "7000",
            ),
            (
                "Bulk Laundry",
                "Cost-effective laundry support for families, hostels, and busy home settings.",
                "6000",
            ),
            (
                "Curtain Cleaning",
                "Gentle cleaning for curtains and drapes that restores freshness and removes dust.",
                "8000",
            ),
            (
                "Beddings and Towels",
                "Fresh cleaning for linens, towels, and soft household essentials.",
                "5000",
            ),
            (
                "Express Laundry",
                "Fast turnaround laundry service for urgent clothing needs and last-minute plans.",
                "6500",
            ),
            (
                "Stain Removal",
                "Targeted stain treatment for garments that need extra attention and care.",
                "5500",
            ),
            (
                "Uniform Laundry",
                "Reliable cleaning for school, office, and work uniforms with neat finishing.",
                "4500",
            ),
            (
                "Fabric Care Service",
                "Gentle handling for delicate fabrics that need expert washing and drying.",
                "7500",
            ),
        ],
        "Moving Services": [
            (
                "Home Relocation Service",
                "Packing, loading, and moving support that makes residential moves less stressful and better organized.",
                "70000",
            ),
            (
                "Office Relocation",
                "Efficient moving help for offices, desks, equipment, and small business setups.",
                "80000",
            ),
            (
                "Packing Assistance",
                "Careful packing of valuables, kitchen items, and fragile belongings for secure transit.",
                "30000",
            ),
            (
                "Furniture Moving",
                "Safe transport for heavy furniture with proper handling and placement support.",
                "28000",
            ),
            (
                "Apartment Move",
                "Simple and affordable moving service for smaller homes and compact apartments.",
                "35000",
            ),
            (
                "Storage Move",
                "Reliable transfer of goods to storage facilities with careful loading and unloading.",
                "32000",
            ),
            (
                "Local Delivery Assist",
                "Quick and practical moving support for short-distance deliveries within the town.",
                "22000",
            ),
            (
                "Event Equipment Move",
                "Handling for tents, chairs, and event materials with organized setup and breakdown.",
                "26000",
            ),
            (
                "Weekend Relocation",
                "Flexible moving service planned around your schedule for smoother weekend transitions.",
                "38000",
            ),
            (
                "Fragile Item Move",
                "Special handling for delicate items that need extra care during transit.",
                "24000",
            ),
        ],
        "Electrical": [
            (
                "House Rewiring",
                "Full electrical rewiring for older homes, improving safety, efficiency, and long-term reliability.",
                "50000",
            ),
            (
                "Ceiling Fan Installation",
                "Neat installation of ceiling fans for improved airflow and better room comfort.",
                "14000",
            ),
            (
                "Socket and Switch Repair",
                "Quick fixes for loose outlets, faulty switches, and aging electrical points.",
                "12000",
            ),
            (
                "Lighting Upgrade",
                "Modern lighting installations for brighter, more stylish interiors and workspaces.",
                "18000",
            ),
            (
                "Outdoor Wiring",
                "Safe wiring solutions for gates, compound lighting, and exterior power needs.",
                "26000",
            ),
            (
                "Power Surge Protection",
                "Installation of protection systems that help guard sensitive appliances against voltage issues.",
                "22000",
            ),
            (
                "Generator Connection",
                "Professional connection setup for generators with proper safety checks and stable performance.",
                "32000",
            ),
            (
                "Electrical Inspection",
                "Detailed inspection services that help identify faults before they become expensive repairs.",
                "16000",
            ),
            (
                "New Circuit Installation",
                "Custom installation for additional power points and dedicated circuits in busy homes.",
                "30000",
            ),
            (
                "Emergency Electrical Fix",
                "Prompt troubleshooting for power failures, sparks, and urgent electrical concerns.",
                "21000",
            ),
        ],
        "Generator Repair": [
            (
                "Generator Maintenance",
                "Routine servicing that keeps generators running smoothly and reduces the risk of sudden failure.",
                "20000",
            ),
            (
                "Fuel System Service",
                "Inspection and cleaning of fuel components to improve efficiency and steady operation.",
                "17000",
            ),
            (
                "Battery Replacement",
                "Fresh battery installation to restore dependable starting power and reliable performance.",
                "14000",
            ),
            (
                "Startup Troubleshooting",
                "Diagnosis of startup issues so your generator can come alive when you need it most.",
                "16000",
            ),
            (
                "Cooling System Repair",
                "Repair of overheating issues to protect the engine and extend generator life.",
                "19000",
            ),
            (
                "Alternator Repair",
                "Skilled alternator servicing to maintain steady electrical output and power stability.",
                "24000",
            ),
            (
                "Commercial Generator Service",
                "Maintenance support for businesses with regular power needs and high reliability expectations.",
                "30000",
            ),
            (
                "Transfer Switch Setup",
                "Professional integration of generator switches for safe and smooth power changes.",
                "28000",
            ),
            (
                "Generator Tune-Up",
                "Comprehensive tune-up service that improves performance, fuel efficiency, and durability.",
                "23000",
            ),
            (
                "Emergency Generator Repair",
                "Fast-response repair service for sudden breakdowns and urgent power restoration needs.",
                "26000",
            ),
        ],
        "Phone Repair": [
            (
                "Android Phone Repair",
                "Screen, battery, and hardware repairs tailored to common smartphone issues and everyday usage.",
                "10000",
            ),
            (
                "iPhone Screen Fix",
                "Professional screen replacement and display repair for cracked or unresponsive devices.",
                "15000",
            ),
            (
                "Battery Replacement",
                "Long-lasting battery upgrades that improve phone performance and daily reliability.",
                "8000",
            ),
            (
                "Charging Port Repair",
                "Repair of damaged charging ports to restore fast and consistent charging.",
                "9000",
            ),
            (
                "Water Damage Recovery",
                "Careful cleaning and restoration for phones affected by liquid damage.",
                "12000",
            ),
            (
                "Software Troubleshooting",
                "Diagnosis and repair of app glitches, boot problems, and system slowdowns.",
                "7000",
            ),
            (
                "Camera Module Repair",
                "Fixes for blurry cameras, shutter issues, and damaged rear camera units.",
                "11000",
            ),
            (
                "Phone Data Transfer",
                "Safe transfer of contacts, media, and files to a new device with minimal effort.",
                "6000",
            ),
            (
                "Phone Unlocking",
                "Trusted unlocking service for supported devices with simple and secure procedures.",
                "10000",
            ),
            (
                "Screen Protector Installation",
                "Professional installation of protective glass to keep phones safe from everyday wear.",
                "5000",
            ),
        ],
        "Computer Repair": [
            (
                "Laptop Repair",
                "Hardware and software troubleshooting for slow, damaged, or unstable laptops.",
                "12000",
            ),
            (
                "Desktop Maintenance",
                "Routine servicing for desktops that improves performance, cooling, and reliability.",
                "14000",
            ),
            (
                "Virus Removal",
                "Careful malware cleanup and security checks to help restore safe computer use.",
                "10000",
            ),
            (
                "SSD Upgrade",
                "Fast storage upgrade service that boosts speed, responsiveness, and file access.",
                "18000",
            ),
            (
                "Keyboard Replacement",
                "Replacement of worn or broken keyboards for smooth typing and better comfort.",
                "8000",
            ),
            (
                "Screen Replacement",
                "Professional screen repair for laptops and monitors with clear, dependable results.",
                "16000",
            ),
            (
                "Data Recovery",
                "Careful recovery support for inaccessible files and important system data.",
                "22000",
            ),
            (
                "Printer Setup",
                "Installation and troubleshooting for printers and home office networking needs.",
                "9000",
            ),
            (
                "Software Installation",
                "Setup of essential software and drivers tailored to your work and learning needs.",
                "7000",
            ),
            (
                "Laptop Cooling Service",
                "Cleaning and maintenance that prevents overheating and helps extend device life.",
                "10000",
            ),
        ],
        "Tutoring": [
            (
                "Mathematics Home Tutor",
                "Patient one-on-one help for secondary school students who need clearer explanations and steady practice.",
                "25000",
            ),
            (
                "English Language Tutor",
                "Support for grammar, comprehension, essay writing, and spoken communication skills.",
                "22000",
            ),
            (
                "Science Revision Class",
                "Focused lessons in biology, chemistry, and physics that make complex topics easier to grasp.",
                "24000",
            ),
            (
                "Exam Prep Coaching",
                "Targeted preparation for school exams with practical study strategies and review sessions.",
                "26000",
            ),
            (
                "Junior Secondary Tutor",
                "Structured tutoring for younger learners building confidence in core school subjects.",
                "20000",
            ),
            (
                "Online Homework Support",
                "Flexible online guidance for assignments, projects, and revision planning.",
                "18000",
            ),
            (
                "Reading Improvement",
                "Skill-building sessions that improve reading speed, comprehension, and confidence.",
                "19000",
            ),
            (
                "Essay Writing Coach",
                "Step-by-step support for writing clear, organized, and well-structured essays.",
                "21000",
            ),
            (
                "Study Skills Coaching",
                "Practical lessons that help students manage time, stay organized, and study effectively.",
                "17000",
            ),
            (
                "Primary School Tutor",
                "Friendly tutoring for foundational subjects with patient explanations and steady encouragement.",
                "16000",
            ),
        ],
        "Laundry": [
            (
                "Laundry Pickup Service",
                "Convenient pickup and delivery for clothes, bedsheets, and daily laundry needs.",
                "5000",
            ),
            (
                "Wash and Iron",
                "Careful washing and ironing for shirts, uniforms, and household clothing.",
                "4000",
            ),
            (
                "Dry Cleaning",
                "Professional cleaning for delicate clothes that need extra care and finishing.",
                "7000",
            ),
            (
                "Bulk Laundry",
                "Cost-effective laundry support for families, hostels, and busy home settings.",
                "6000",
            ),
            (
                "Curtain Cleaning",
                "Gentle cleaning for curtains and drapes that restores freshness and removes dust.",
                "8000",
            ),
            (
                "Beddings and Towels",
                "Fresh cleaning for linens, towels, and soft household essentials.",
                "5000",
            ),
            (
                "Express Laundry",
                "Fast turnaround laundry service for urgent clothing needs and last-minute plans.",
                "6500",
            ),
            (
                "Stain Removal",
                "Targeted stain treatment for garments that need extra attention and care.",
                "5500",
            ),
            (
                "Uniform Laundry",
                "Reliable cleaning for school, office, and work uniforms with neat finishing.",
                "4500",
            ),
            (
                "Fabric Care Service",
                "Gentle handling for delicate fabrics that need expert washing and drying.",
                "7500",
            ),
        ],
        "Moving Services": [
            (
                "Home Relocation Service",
                "Packing, loading, and moving support that makes residential moves less stressful and better organized.",
                "70000",
            ),
            (
                "Office Relocation",
                "Efficient moving help for offices, desks, equipment, and small business setups.",
                "80000",
            ),
            (
                "Packing Assistance",
                "Careful packing of valuables, kitchen items, and fragile belongings for secure transit.",
                "30000",
            ),
            (
                "Furniture Moving",
                "Safe transport for heavy furniture with proper handling and placement support.",
                "28000",
            ),
            (
                "Apartment Move",
                "Simple and affordable moving service for smaller homes and compact apartments.",
                "35000",
            ),
            (
                "Storage Move",
                "Reliable transfer of goods to storage facilities with careful loading and unloading.",
                "32000",
            ),
            (
                "Local Delivery Assist",
                "Quick and practical moving support for short-distance deliveries within the town.",
                "22000",
            ),
            (
                "Event Equipment Move",
                "Handling for tents, chairs, and event materials with organized setup and breakdown.",
                "26000",
            ),
            (
                "Weekend Relocation",
                "Flexible moving service planned around your schedule for smoother weekend transitions.",
                "38000",
            ),
            (
                "Fragile Item Move",
                "Special handling for delicate items that need extra care during transit.",
                "24000",
            ),
        ],
        "Home Painting": [
            (
                "Interior Wall Painting",
                "Professional painting for living rooms, bedrooms, and hallways with smooth, lasting finishes.",
                "60000",
            ),
            (
                "Exterior House Painting",
                "Weather-resistant paint application that refreshes the outside of your home.",
                "75000",
            ),
            (
                "Kitchen Cabinet Painting",
                "Clean, modern repainting for cabinets that gives kitchens a fresh new look.",
                "35000",
            ),
            (
                "Room Makeover Paint",
                "Quick color refresh for a single room with neat prep and tidy completion.",
                "25000",
            ),
            (
                "Ceiling Painting",
                "Careful ceiling repainting that brightens rooms and hides old marks.",
                "22000",
            ),
            (
                "Decorative Wall Finish",
                "Stylish painting options for feature walls and creative interior accents.",
                "30000",
            ),
            (
                "Fence Painting",
                "Protective coating service for fences that improves appearance and durability.",
                "18000",
            ),
            (
                "Office Wall Painting",
                "Professional finish for office interiors that keeps workspaces bright and polished.",
                "40000",
            ),
            (
                "Touch-Up Painting",
                "Small-scale repainting for scratches, stains, and minor surface imperfections.",
                "15000",
            ),
            (
                "Waterproof Paint Service",
                "Durable coating for humid areas that helps protect walls from moisture damage.",
                "28000",
            ),
        ],
        "Car Repair": [
            (
                "Vehicle Diagnostics",
                "Computerized diagnosis of engine and system faults so the right repair is done quickly.",
                "15000",
            ),
            (
                "Brake Service",
                "Inspection and maintenance of brake systems for safe and dependable stopping power.",
                "20000",
            ),
            (
                "Oil Change",
                "Regular oil and filter change service that helps engines stay efficient and healthy.",
                "12000",
            ),
            (
                "Battery Replacement",
                "Reliable battery replacement to restore strong starts and consistent performance.",
                "14000",
            ),
            (
                "Engine Tune-Up",
                "Comprehensive tune-up service that improves efficiency, smoothness, and fuel economy.",
                "26000",
            ),
            (
                "AC Car Repair",
                "Repairs and servicing for vehicle air conditioning systems to keep cabins cool.",
                "18000",
            ),
            (
                "Suspension Fix",
                "Repair of shocks and suspension parts for better ride quality and stability.",
                "22000",
            ),
            (
                "Wheel Alignment",
                "Precise alignment service that improves handling, tire life, and driving comfort.",
                "16000",
            ),
            (
                "Tyre Change",
                "Fast replacement of worn tyres with quality options suited to your car and road use.",
                "18000",
            ),
            (
                "Electrical Fault Repair",
                "Diagnosis and repair of lighting, wiring, and dashboard electrical issues.",
                "17000",
            ),
        ],
        "Photography": [
            (
                "Event Photography",
                "Professional coverage for weddings, birthdays, and social events with polished and memorable results.",
                "50000",
            ),
            (
                "Portrait Session",
                "Creative portrait photography for family, business, and personal branding needs.",
                "30000",
            ),
            (
                "Wedding Coverage",
                "Complete wedding photography service that captures key moments with elegance and detail.",
                "65000",
            ),
            (
                "Birthday Shoot",
                "Bright and fun photography for children, teens, and adults celebrating special occasions.",
                "25000",
            ),
            (
                "Corporate Headshots",
                "Professional image sessions for teams, executives, and business profiles.",
                "22000",
            ),
            (
                "Product Photography",
                "Clear product shoots designed to highlight features for online stores and promotions.",
                "28000",
            ),
            (
                "Outdoor Lifestyle Shoot",
                "Natural photography sessions for fashion, travel, and personal storytelling outdoors.",
                "35000",
            ),
            (
                "Studio Photography",
                "Controlled studio sessions with lighting and backdrops for striking images.",
                "32000",
            ),
            (
                "Drone Photography",
                "Aerial images for properties, events, and wide-angle landscapes with cinematic framing.",
                "45000",
            ),
            (
                "Video Coverage",
                "Short-form video capture for events, promotions, and memorable highlight reels.",
                "40000",
            ),
        ],
        "Catering": [
            (
                "Birthday Catering",
                "Delicious catering for birthdays with appealing menu options, neat presentation, and dependable service.",
                "80000",
            ),
            (
                "Wedding Catering",
                "Elegant food service for weddings with assorted dishes planned for guest comfort and celebration.",
                "120000",
            ),
            (
                "Corporate Catering",
                "Professional catering for meetings, workshops, and business events with efficient delivery.",
                "70000",
            ),
            (
                "Small Party Catering",
                "Flexible catering for intimate parties with tasty meals that still feel special.",
                "50000",
            ),
            (
                "Lunch Box Catering",
                "Convenient meal service for offices, schools, and group events with balanced menu choices.",
                "30000",
            ),
            (
                "Dessert Catering",
                "Sweet catering service for events, complete with pastries, cakes, and bite-sized treats.",
                "25000",
            ),
            (
                "Traditional Food Catering",
                "Authentic local dishes prepared for gatherings with warm hospitality and rich flavors.",
                "60000",
            ),
            (
                "Outdoor Catering",
                "Reliable food service for outdoor celebrations with practical setup and easy serving.",
                "65000",
            ),
            (
                "Buffet Catering",
                "Stylish buffet service that keeps guests comfortable and offers a broad selection of dishes.",
                "85000",
            ),
            (
                "Premium Catering",
                "High-end catering for special occasions with refined presentation and premium menu options.",
                "150000",
            ),
        ],
        "Event Planning": [
            (
                "Wedding Planning",
                "Complete wedding planning support with coordination, vendor management, and smooth event flow.",
                "150000",
            ),
            (
                "Birthday Party Planning",
                "Organized celebration planning for themes, decor, logistics, and guest experience.",
                "60000",
            ),
            (
                "Corporate Event Planning",
                "Professional planning for conferences, launches, and business gatherings with polished execution.",
                "100000",
            ),
            (
                "Conference Setup",
                "Detailed event coordination for meetings that need clear schedules, seating, and logistics.",
                "80000",
            ),
            (
                "Decor and Styling",
                "Creative planning for interiors, theme design, and beautiful event presentation.",
                "50000",
            ),
            (
                "Guest Management",
                "Structured guest coordination for smooth arrivals, seating, and special arrangements.",
                "45000",
            ),
            (
                "Vendor Coordination",
                "Planning support that connects trusted vendors for catering, decor, and entertainment.",
                "55000",
            ),
            (
                "Event Budget Planning",
                "Practical budgeting guidance that keeps celebrations organized without overspending.",
                "40000",
            ),
            (
                "Outdoor Event Planning",
                "Planning for garden, park, and open-air events with weather-conscious logistics.",
                "70000",
            ),
            (
                "Anniversary Planning",
                "Elegant planning for anniversaries with attention to decor, timing, and memorable details.",
                "65000",
            ),
        ],
        "Hair Styling": [
            (
                "Hair Styling",
                "Professional haircuts and styling for everyday looks, events, and personal grooming needs.",
                "12000",
            ),
            (
                "Braiding Service",
                "Neat braiding and protective styling for a polished and long-lasting look.",
                "10000",
            ),
            (
                "Hair Treatment",
                "Conditioning and treatment services that improve softness, shine, and overall hair health.",
                "15000",
            ),
            (
                "Blowout Styling",
                "Smooth and sleek styling for special occasions and everyday confidence.",
                "8000",
            ),
            (
                "Wash and Set",
                "Fresh wash-and-set styling for neat, manageable hair with a polished finish.",
                "7000",
            ),
            (
                "Hair Coloring",
                "Professional coloring that refreshes your style with careful application and color matching.",
                "20000",
            ),
            (
                "Weave Installation",
                "Beautiful weave styling for volume, texture, and long-lasting appearance.",
                "18000",
            ),
            (
                "Hair Makeup Combo",
                "Coordinated styling and makeup service for events and photo-ready looks.",
                "22000",
            ),
            (
                "Children's Hair Styling",
                "Gentle and tidy styling services designed for kids and younger clients.",
                "6000",
            ),
            (
                "Curly Hair Care",
                "Specialized care and styling for curly hair textures with defined and healthy results.",
                "13000",
            ),
        ],
        "Makeup Artist": [
            (
                "Professional Makeup",
                "Bridal and event makeup that creates a polished look with long-lasting wear and careful detail.",
                "25000",
            ),
            (
                "Bridal Makeup",
                "Elegant bridal makeup designed for beauty, comfort, and photography-ready finish.",
                "30000",
            ),
            (
                "Party Makeup",
                "Glowing makeup for birthdays, dinners, and festive gatherings with a fresh look.",
                "18000",
            ),
            (
                "Photoshoot Makeup",
                "Flawless makeup tailored for studio shoots and professional portrait sessions.",
                "22000",
            ),
            (
                "Natural Glow Makeup",
                "Subtle everyday makeup that enhances features while keeping the finish soft and natural.",
                "15000",
            ),
            (
                "Editorial Makeup",
                "Creative makeup styling for fashion, media, and statement-event appearances.",
                "28000",
            ),
            (
                "Airbrush Makeup",
                "Smooth and long-wear makeup suitable for events that need a refined, camera-ready finish.",
                "26000",
            ),
            (
                "Makeup Trial Session",
                "A practice session to refine colors, style, and comfort before your main event.",
                "12000",
            ),
            (
                "Wedding Party Makeup",
                "Coordinated beauty services for bridesmaids and guests to match the wedding look.",
                "24000",
            ),
            (
                "Special Occasion Makeup",
                "Versatile makeup for anniversaries, graduations, and important celebrations.",
                "20000",
            ),
        ],
        "Interior Design": [
            (
                "Living Room Styling",
                "Thoughtful interior styling that improves comfort, flow, and visual balance in shared spaces.",
                "40000",
            ),
            (
                "Kitchen Design",
                "Practical kitchen design ideas that blend function, storage, and modern appeal.",
                "50000",
            ),
            (
                "Bedroom Makeover",
                "Elegant bedroom design concepts that make spaces feel restful, organized, and inviting.",
                "45000",
            ),
            (
                "Office Interior Design",
                "Functional office layouts that support productivity while keeping the environment polished and welcoming.",
                "55000",
            ),
            (
                "Color Consultation",
                "Professional guidance on colors, tones, and palettes that suit your home and personal style.",
                "20000",
            ),
            (
                "Furniture Arrangement",
                "Smart layout planning that helps rooms feel more spacious, practical, and visually appealing.",
                "25000",
            ),
            (
                "Lighting Design",
                "Interior lighting concepts that improve mood, visibility, and overall room atmosphere.",
                "30000",
            ),
            (
                "Wardrobe Design",
                "Customized storage solutions that make bedrooms and dressing areas more efficient.",
                "35000",
            ),
            (
                "Space Planning",
                "Careful planning for better room flow, utility, and comfort in homes and offices.",
                "32000",
            ),
            (
                "Home Styling Package",
                "A complete styling plan that brings together decor, color, and layout for a cohesive finish.",
                "60000",
            ),
        ],
        "Security Services": [
            (
                "Security Camera Installation",
                "CCTV setup for homes and businesses with clear coverage and reliable monitoring support.",
                "75000",
            ),
            (
                "Alarm System Setup",
                "Professional installation of alarms that strengthen protection for entrances and sensitive areas.",
                "60000",
            ),
            (
                "Door Access Control",
                "Secure access solutions for homes, offices, and private properties with controlled entry.",
                "50000",
            ),
            (
                "Gate Security Installation",
                "Robust gate and perimeter security installation for homes and commercial premises.",
                "65000",
            ),
            (
                "Night Patrol Service",
                "Scheduled security patrols for neighborhoods, shops, and residential estates.",
                "40000",
            ),
            (
                "Event Security",
                "Trained security support for social events, private functions, and public gatherings.",
                "45000",
            ),
            (
                "Security Consultation",
                "Assessment of weak points and practical suggestions for stronger protection.",
                "30000",
            ),
            (
                "Intercom System Setup",
                "Modern intercom installation that improves visitor communication and property control.",
                "35000",
            ),
            (
                "Perimeter Lighting",
                "Security lighting designed to increase visibility and deter intrusion around properties.",
                "28000",
            ),
            (
                "Emergency Security Response",
                "Rapid support for urgent site protection needs and immediate security concerns.",
                "42000",
            ),
        ],
        "Air Conditioner Repair": [
            (
                "Air Conditioner Servicing",
                "Regular AC cleaning and maintenance that improves cooling performance and energy efficiency.",
                "15000",
            ),
            (
                "Refrigerant Recharge",
                "Professional recharge service that restores efficient cooling and better air output.",
                "22000",
            ),
            (
                "Fan Motor Repair",
                "Repair of AC fan systems that keeps cooling units operating smoothly and quietly.",
                "18000",
            ),
            (
                "Filter Replacement",
                "Quick replacement of filters for cleaner air and better airflow in your space.",
                "8000",
            ),
            (
                "Gas Leak Check",
                "Careful diagnosis of cooling systems to ensure safe and reliable operation.",
                "20000",
            ),
            (
                "Installation Service",
                "Professional installation of split units and window ACs with neat setup and testing.",
                "25000",
            ),
            (
                "Emergency Cooling Repair",
                "Fast repair support for sudden breakdowns and uncomfortable indoor temperatures.",
                "23000",
            ),
            (
                "Duct Cleaning",
                "Cleaning of AC ducts to improve airflow, cleanliness, and indoor air quality.",
                "17000",
            ),
            (
                "Thermostat Replacement",
                "New thermostat installation for better temperature control and energy management.",
                "14000",
            ),
            (
                "Annual Maintenance Plan",
                "Scheduled maintenance for long-term AC reliability and consistent cooling performance.",
                "19000",
            ),
        ],
        "Furniture Repair": [
            (
                "Furniture Restoration",
                "Repair and restoration of sofas, chairs, and cabinets to bring life back to worn pieces.",
                "22000",
            ),
            (
                "Wood Refinishing",
                "Sanding and refinishing that restores wood furniture with a smooth and polished look.",
                "26000",
            ),
            (
                "Loose Joint Fix",
                "Professional tightening of joints and fittings to improve durability and stability.",
                "9000",
            ),
            (
                "Upholstery Repair",
                "Repair and re-stitching for damaged upholstery that keeps furniture comfortable and presentable.",
                "18000",
            ),
            (
                "Table Rebuild",
                "Full rebuilding of table frames and surfaces for stronger, longer-lasting furniture.",
                "24000",
            ),
            (
                "Chair Repair",
                "Simple and dependable repair for worn chairs, legs, and support structures.",
                "11000",
            ),
            (
                "Cabinet Door Fix",
                "Adjustment and repair of cabinet doors for better use, alignment, and appearance.",
                "13000",
            ),
            (
                "Antique Restoration",
                "Careful restoration for older furniture pieces that need gentle handling and expert treatment.",
                "30000",
            ),
            (
                "Polishing Service",
                "Furniture polishing that refreshes surfaces and brings out the natural finish.",
                "10000",
            ),
            (
                "Custom Furniture Repair",
                "Tailored repair services for unique furniture pieces that need special attention.",
                "28000",
            ),
        ],
    }
    locations = [
        "Igbeba",
        "Molipa",
        "Oke-Aje",
        "Oke-Owa",
        "Odo-Esa",
        "Imowo",
        "Ayetoro",
        "Itantebo",
        "Porogun",
        "Ijasi",
        "Awa",
        "Isiwo",
        "Ago-Iwoye",
        "Ijebu-Igbo",
        "Isonyin",
        "Ijebu-Imusin",
        "Oru",
        "Imagbon",
        "Ilaporu",
    ]

    providers_map = {
        "Cleaning": "Bright Cleaning Services",
        "Plumbing": "Swift Plumbing Works",
        "Electrical": "Adebayo Electricals",
        "Generator Repair": "PowerGen Experts",
        "Phone Repair": "Mobile Doctor Repairs",
        "Computer Repair": "Laptop Rescue Center",
        "Tutoring": "Prime Tutors Academy",
        "Laundry": "Spark Laundry Hub",
        "Moving Services": "MoveEasy Logistics",
        "Home Painting": "Master Painters",
        "Car Repair": "AutoCare Garage",
        "Photography": "Vision Photography",
        "Catering": "Golden Caterers",
        "Event Planning": "Elite Event Planners",
        "Hair Styling": "Hair Palace",
        "Makeup Artist": "Beauty Touch Studio",
        "Interior Design": "Stylish Spaces Interiors",
        "Security Services": "SecureHome Systems",
        "Air Conditioner Repair": "CoolAir Solutions",
        "Furniture Repair": "QuickFix Furniture",
    }

    services = []
    for category_name, entries in category_service_templates.items():
        provider_name = providers_map.get(category_name, "Local Service Provider")
        for index, (service_name, service_detail, price) in enumerate(entries):
            location_area = locations[index % len(locations)]
            services.append(
                {
                    "title": provider_name,
                    "description": f"{service_detail}",
                    "price": price,
                    "category": category_name,
                    "provider": provider_name,
                    "location": location_area,
                    "image_url": SERVICE_IMAGE_MAP.get(
                        category_name, "assets/img/gallery/list1.png"
                    ),
                }
            )
    return services


services = build_services()


def _normalize_value(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return value.strip() or None


def _parse_float(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    try:
        return float(value.strip())
    except (ValueError, TypeError):
        return None


def _get_or_create_imported_category(db):
    category_name = "Imported Listing"
    category = db.query(Category).filter(Category.name == category_name).first()
    if category:
        return category

    category = Category(
        name=category_name,
        description="Placeholder category for imported providers without a service category.",
        image_url="assets/img/gallery/list1.png",
    )
    db.add(category)
    db.flush()
    return category


def _format_display_name(value: Optional[str]) -> str:
    if not value:
        return ""

    words = value.strip().split()
    if not words:
        return ""

    formatted_words = []
    for word in words:
        if word.isupper() or word.islower() and len(word) <= 3:
            formatted_words.append(word)
        else:
            formatted_words.append(word[:1].upper() + word[1:].lower())
    return " ".join(formatted_words)


def _normalize_placeholder_service_title(title: Optional[str], provider_name: Optional[str]) -> str:
    if not title:
        return _format_display_name(provider_name) or "Imported Provider"

    normalized_title = title.strip()
    if not normalized_title:
        return _format_display_name(provider_name) or "Imported Provider"

    suffix_pattern = re.compile(r"\s+(placeholder|placeholder service)\s*$", re.IGNORECASE)
    cleaned_title = suffix_pattern.sub("", normalized_title).strip()
    if cleaned_title:
        return _format_display_name(cleaned_title)

    return _format_display_name(provider_name) or "Imported Provider"


def _create_placeholder_service_for_provider(db, provider, category, location_id=None):
    existing_service = (
        db.query(Service)
        .filter(Service.provider_id == provider.id)
        .first()
    )
    if existing_service:
        return existing_service

    display_name = _normalize_placeholder_service_title(
        provider.business_name,
        provider.business_name,
    )
    service = Service(
        title=display_name or "Imported Provider",
        description="Placeholder service created to surface this imported provider in search results.",
        price="Contact for pricing",
        image_url=category.image_url,
        provider=provider,
        category=category,
        location_id=location_id,
    )
    db.add(service)
    return service


def ensure_placeholder_services_for_imported_providers(db, imported_from=None, location_ids_by_provider_name=None):
    category = _get_or_create_imported_category(db)
    placeholder_count = 0
    query = db.query(Provider).filter(Provider.is_imported.is_(True))
    if imported_from:
        query = query.filter(Provider.imported_from == imported_from)

    location_ids_by_provider_name = location_ids_by_provider_name or {}

    for provider in query.all():
        has_service = db.query(Service).filter(Service.provider_id == provider.id).first()
        location_id = None
        if location_ids_by_provider_name:
            location_id = location_ids_by_provider_name.get(provider.business_name)

        if not has_service:
            _create_placeholder_service_for_provider(db, provider, category, location_id=location_id)
            placeholder_count += 1
        elif location_id is not None and has_service.location_id is None:
            has_service.location_id = location_id

    if placeholder_count > 0 or location_ids_by_provider_name:
        db.commit()
    return placeholder_count


def import_seed_providers_from_csv(csv_filename: Optional[str] = None) -> None:
    if csv_filename is None:
        csv_filename = os.path.join(
            ROOT_DIR,
            "seed",
            "Free Nigeria Business List export 2026-08-04 22-44-59.csv",
        )

    csv_path = Path(csv_filename)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_filename}")

    imported_from = csv_path.stem
    inserted = 0
    skipped = 0
    skipped_invalid = 0
    location_ids_by_provider_name = {}

    db = SessionLocal()
    try:
        existing_providers = db.query(Provider).all()
        existing_names = {
            provider.business_name.strip().lower()
            for provider in existing_providers
            if provider.business_name
        }
        existing_emails = {
            provider.email.strip().lower()
            for provider in existing_providers
            if provider.email
        }

        print(f"Importing providers from CSV: {csv_path.resolve()}")
        with csv_path.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row_number, row in enumerate(reader, start=1):
                business_name = _normalize_value(
                    row.get("Business Name")
                    or row.get("business_name")
                    or row.get("BusinessName")
                    or row.get("name")
                )
                if not business_name:
                    skipped += 1
                    skipped_invalid += 1
                    continue

                email = _normalize_value(
                    row.get("Email")
                    or row.get("email")
                    or row.get("Email Address")
                )
                phone = _normalize_value(
                    row.get("Phone")
                    or row.get("phone")
                    or row.get("Phone Number")
                    or row.get("telephone")
                    or row.get("mobile")
                    or row.get("mobile_number")
                ) or ""

                website = _normalize_value(
                    row.get("Website")
                    or row.get("website")
                    or row.get("Website URL")
                )
                linkedin_url = _normalize_value(
                    row.get("LinkedIn")
                    or row.get("linkedin")
                    or row.get("LinkedIn URL")
                    or row.get("linkedin_url")
                )
                about = _normalize_value(
                    row.get("Description")
                    or row.get("About")
                    or row.get("About Us")
                    or row.get("industry")
                )
                area = _normalize_value(
                    row.get("Area")
                    or row.get("area")
                    or row.get("Neighborhood")
                    or row.get("locality")
                )
                city = _normalize_value(
                    row.get("City")
                    or row.get("city")
                    or row.get("Town")
                    or row.get("locality")
                )
                state = _normalize_value(
                    row.get("State")
                    or row.get("state")
                    or row.get("Province")
                    or row.get("region")
                )
                address = _normalize_value(
                    row.get("Address")
                    or row.get("address")
                    or row.get("Street Address")
                )
                longitude = _parse_float(
                    row.get("Longitude") or row.get("longitude")
                )
                latitude = _parse_float(
                    row.get("Latitude") or row.get("latitude")
                )

                normalized_name = business_name.lower()
                normalized_email = email.lower() if email else None
                if normalized_name in existing_names or (
                    normalized_email and normalized_email in existing_emails
                ):
                    skipped += 1
                    continue

                provider = Provider(
                    business_name=business_name,
                    phone=phone,
                    email=email.lower() if email else None,
                    website=website,
                    linkedin_url=linkedin_url,
                    about=about,
                    is_imported=True,
                    imported_from=imported_from,
                    verified=False,
                )
                db.add(provider)
                db.flush()

                if city and state:
                    location = Location(
                        area=area,
                        city=city,
                        state=state,
                        address=address,
                        longitude=longitude,
                        latitude=latitude,
                    )
                    db.add(location)
                    db.flush()
                    location_ids_by_provider_name[business_name] = location.id

                existing_names.add(normalized_name)
                if normalized_email:
                    existing_emails.add(normalized_email)
                inserted += 1

        placeholder_count = ensure_placeholder_services_for_imported_providers(
            db,
            imported_from=imported_from,
            location_ids_by_provider_name=location_ids_by_provider_name,
        )
        if inserted == 0 and skipped > 0:
            print(
                f"No new providers were added from CSV because the same rows already exist in the database. "
                f"Skipped {skipped} duplicates and {skipped_invalid} invalid rows."
            )
        else:
            print(
                f"Imported {inserted} providers from CSV, skipped {skipped} duplicates, and skipped {skipped_invalid} invalid rows."
            )
        if placeholder_count > 0:
            print(f"Created {placeholder_count} placeholder services for imported providers without services.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_tables() -> None:
    ensure_schema(engine)


def seed() -> None:
    db = SessionLocal()
    try:
        for category_data in categories:
            existing = (
                db.query(Category)
                .filter(Category.name == category_data["name"])
                .first()
            )
            if not existing:
                db.add(
                    Category(
                        name=category_data["name"],
                        description=category_data["description"],
                        image_url=category_data["image_url"],
                    )
                )

        for location_data in locations:
            existing = (
                db.query(Location)
                .filter(
                    Location.area == location_data["area"],
                    Location.city == location_data["city"],
                    Location.state == location_data["state"],
                )
                .first()
            )
            if not existing:
                db.add(Location(**location_data))

        for provider_data in providers:
            existing = (
                db.query(Provider)
                .filter(Provider.business_name == provider_data["business_name"])
                .first()
            )
            if not existing:
                provider_data_with_metadata = {
                    **provider_data,
                    "is_imported": True,
                    "imported_from": provider_data.get("imported_from", "seed"),
                }
                db.add(Provider(**provider_data_with_metadata))

        db.commit()

        categories_map = {
            category.name: category.id for category in db.query(Category).all()
        }

        providers_map = {
            provider.business_name: provider.id for provider in db.query(Provider).all()
        }

        locations_map = {
            location.area: location.id for location in db.query(Location).all()
        }

        for service_data in services:
            category_id = categories_map.get(service_data["category"])
            provider_id = providers_map.get(service_data["provider"])
            location_id = locations_map.get(service_data["location"])

            if category_id is None or provider_id is None or location_id is None:
                continue

            category = db.get(Category, category_id)
            provider = db.get(Provider, provider_id)
            location = db.get(Location, location_id)

            if not category or not provider or not location:
                continue
            existing_service = (
                db.query(Service).filter(Service.title == service_data["title"]).first()
            )
            if existing_service:
                existing_service.description = service_data["description"]
                existing_service.price = service_data["price"]
                existing_service.image_url = service_data.get(
                    "image_url",
                    "assets/img/gallery/list1.png",
                )
                existing_service.category = category
                existing_service.provider = provider
                existing_service.location = location
            else:
                db.add(
                    Service(
                        title=service_data["title"],
                        description=service_data["description"],
                        price=service_data["price"],
                        image_url=service_data.get(
                            "image_url", "assets/img/gallery/list1.png"
                        ),
                        category=category,
                        provider=provider,
                        location=location,
                    )
                )

        db.commit()
        print("Database seeded successfully")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
    seed()
    import_seed_providers_from_csv()
