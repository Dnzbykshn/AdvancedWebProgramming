"""Static CV/Profile data for Deniz Büyükşahin — used as context for the Career Agent."""

PROFILE_DATA = {
    "name": "Deniz Büyükşahin",
    "email": "buyuksahin.dnz@gmail.com",
    "phone": "+90 545 840 0810",
    "location": "Antalya, Turkey",
    "date_of_birth": "2001-08-10",
    "driving_license": "B & A2",
    "github": "github.com/Dnzbykshn",
    "linkedin": "linkedin.com/in/denizbuyuksahin/",
    "profile_summary": (
        "Proactive Computer Engineering student with a solid foundation in both software development "
        "and network administration. Combines hands-on experience in full-stack development (ASP.NET, "
        "Next.js, Python) with practical knowledge of IT infrastructure, Linux systems, and network "
        "security. Certified in CCNA and Cybersecurity, with a passion for automating workflows, "
        "cloud technologies (AWS), and DevSecOps practices. Seeking to leverage technical skills in "
        "system optimization and secure infrastructure to contribute to scalable IT solutions."
    ),
    "work_experience": [
        {
            "company": "RTN House",
            "role": "AI & Product Engineer (Contract)",
            "period": "01/2026 – Present",
            "highlights": [
                "Engineered a Hybrid Search engine using Python (FastAPI), PostgreSQL (pgvector), and Elasticsearch",
                "Integrated Google Gemini LLM for personalized content generation with 3-tier Semantic Routing",
                "Designed Docker-containerized microservices infrastructure with Redis caching, reducing API costs by 60%",
                "Developed end-to-end API services for Flutter/React Native mobile interfaces",
            ],
        },
        {
            "company": "Minimal Yazilim",
            "role": "Full Stack Engineer",
            "period": "12/2025 – Present",
            "highlights": [
                "Architected scalable full-stack solutions for CRM, SCM, and internal control systems",
                "Developed SEO-centric, high-conversion web platforms using Next.js with SSR/SSG",
                "Built secure admin dashboards (CMS) for business operations management",
                "Engineered cross-platform mobile solutions synchronized with web infrastructures",
            ],
        },
        {
            "company": "Huawei Student Developers",
            "role": "Project Team Leader",
            "period": "09/2024 – Present",
            "highlights": [
                "Organized technical software training programs for students",
                "Managed workflows using cloud collaboration tools (Google Workspace)",
            ],
        },
        {
            "company": "Freelance",
            "role": "Full-Stack Developer",
            "period": "09/2022 – Present",
            "highlights": [
                "Directed full SDLC for SME clients: requirements analysis through production deployment",
                "Engineered a Warehouse Management System (WMS) using ASP.NET MVC and MS SQL",
                "Automated reporting features reducing manual stock counting errors by ~30%",
            ],
        },
        {
            "company": "HB Technology",
            "role": "Part-Time IT Technician",
            "period": "2021 – 2024",
            "highlights": [
                "Configured and maintained LAN, routers, and switches",
                "Provided Level-2 support for hardware/software incidents with TCP/IP analysis",
                "Administered IP-based CCTV monitoring systems",
            ],
        },
    ],
    "education": [
        {
            "institution": "Akdeniz University",
            "degree": "Computer Engineering (English)",
            "period": "2024 – Present",
        },
        {
            "institution": "Akdeniz University",
            "degree": "Computer Programming",
            "period": "2022 – 2024",
            "gpa": "3.39 - High Honor Graduate",
        },
        {
            "institution": "Dokuz Eylül University",
            "degree": "Preschool Education",
            "period": "2020 – 2021",
        },
    ],
    "technical_skills": {
        "devops_cloud": "AWS (EC2, S3, IAM), Docker, Git, CI/CD Pipelines, Linux Administration (Bash Scripting)",
        "programming": "Python, Java, C#, JavaScript, OOP, SQL",
        "web_database": "RESTful APIs, ASP.NET MVC, Entity Framework, MS SQL, HTML/CSS, Next.js, FastAPI",
        "network_systems": "TCP/IP, LAN/WAN Administration, Network Troubleshooting, OSI Model, TLS 1.3, AES Encryption",
    },
    "certifications": [
        "Cisco Certified Network Associate (CCNA)",
        "Cisco Introduction to Cybersecurity",
        "NDG Linux Essentials",
    ],
    "projects": [
        {
            "name": "Smart Health Monitoring System (Stanford Univ. Competition Winner)",
            "role": "Project Lead",
            "description": (
                "HIPAA/GDPR compliant data pipeline using Python with AES-128 encryption and TLS 1.3. "
                "Developed RESTful APIs with HL7 FHIR standards. Reduced hardware dependency by 90% "
                "via OpenCV signal processing."
            ),
        },
        {
            "name": "Automated Business Intelligence Harvester with OCR",
            "description": (
                "Data-harvesting engine in Python (Selenium, Requests) with Tesseract OCR pipeline. "
                "Automated extraction from 115+ pages, aggregating 2,000+ company profiles."
            ),
        },
        {
            "name": "High-Frequency Algorithmic Trading Simulation",
            "description": (
                "Real-time trading engine using Python and Asyncio with WebSocket data streams. "
                "Grid-Search algorithm for 300+ strategy configurations. "
                "Recognized as exemplary project by faculty."
            ),
        },
    ],
    "languages": {"English": "Professional Working Proficiency (B2)", "Turkish": "Native"},
    "organizations": [
        "BILMÖK (largest national student congress in Turkey) — Committee organizer for 2025 edition, "
        "developed eligibility-checking algorithm for 700+ participants"
    ],
    "volunteering": [
        {
            "organization": "Habitat Dernegi (Vodafone Foundation partnership)",
            "role": "AI Stars Educator",
            "period": "02/2026 – Present",
            "description": "Educating students on responsible and ethical use of AI",
        }
    ],
}


def get_profile_as_text() -> str:
    """Format the profile data as a readable text string for prompt injection."""
    p = PROFILE_DATA
    lines = [
        f"# {p['name']}",
        f"Email: {p['email']} | Phone: {p['phone']} | Location: {p['location']}",
        f"GitHub: {p['github']} | LinkedIn: {p['linkedin']}",
        "",
        "## Profile Summary",
        p["profile_summary"],
        "",
        "## Work Experience",
    ]

    for exp in p["work_experience"]:
        lines.append(f"\n### {exp['role']} at {exp['company']} ({exp['period']})")
        for h in exp["highlights"]:
            lines.append(f"  - {h}")

    lines.append("\n## Education")
    for edu in p["education"]:
        gpa_str = f" — GPA: {edu['gpa']}" if "gpa" in edu else ""
        lines.append(f"  - {edu['degree']}, {edu['institution']} ({edu['period']}){gpa_str}")

    lines.append("\n## Technical Skills")
    for category, skills in p["technical_skills"].items():
        lines.append(f"  - {category.replace('_', ' ').title()}: {skills}")

    lines.append("\n## Certifications")
    for cert in p["certifications"]:
        lines.append(f"  - {cert}")

    lines.append("\n## Projects")
    for proj in p["projects"]:
        lines.append(f"\n### {proj['name']}")
        lines.append(f"  {proj['description']}")

    lines.append("\n## Languages")
    for lang, level in p["languages"].items():
        lines.append(f"  - {lang}: {level}")

    lines.append("\n## Organizations & Volunteering")
    for org in p["organizations"]:
        lines.append(f"  - {org}")
    for vol in p["volunteering"]:
        lines.append(f"  - {vol['role']} at {vol['organization']} ({vol['period']}): {vol['description']}")

    return "\n".join(lines)
