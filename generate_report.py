"""
GMinsta Academic Report Generator
Generates a fully formatted .docx Word document
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

doc = Document()

# ── Page margins ──────────────────────────────────────────────
for section in doc.sections:
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(3.0)
    section.right_margin  = Cm(2.5)

# ── Helper: set font for a run ────────────────────────────────
def styled_run(para, text, bold=False, italic=False, size=11,
               color=None, underline=False):
    run = para.add_run(text)
    run.bold      = bold
    run.italic    = italic
    run.underline = underline
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = RGBColor(*color)
    return run

# ── Helpers ───────────────────────────────────────────────────
def heading1(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after  = Pt(6)
    styled_run(p, text, bold=True, size=16, color=(131, 58, 180))
    p.paragraph_format.left_indent = Cm(0)
    return p

def heading2(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after  = Pt(4)
    styled_run(p, text, bold=True, size=13, color=(40, 40, 40))
    return p

def heading3(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after  = Pt(2)
    styled_run(p, text, bold=True, size=11, color=(80, 80, 80))
    return p

def body(text, indent=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    if indent:
        p.paragraph_format.left_indent = Cm(0.5)
    styled_run(p, text, size=11)
    return p

def bullet(text, level=0):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Cm(0.5 + level * 0.5)
    styled_run(p, text, size=10.5)
    return p

def divider():
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(4)
    run = p.add_run('─' * 80)
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(200, 200, 200)

def add_table(headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    # Header row
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        for run in hdr[i].paragraphs[0].runs:
            run.bold = True
            run.font.size = Pt(10)
        hdr[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        # shade header
        tc = hdr[i]._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), '833AB4')
        tcPr.append(shd)
    # Data rows
    for r_idx, row_data in enumerate(rows):
        row = table.rows[r_idx + 1].cells
        for c_idx, cell_text in enumerate(row_data):
            row[c_idx].text = cell_text
            for run in row[c_idx].paragraphs[0].runs:
                run.font.size = Pt(10)
    doc.add_paragraph()  # spacing after table

# ══════════════════════════════════════════════════════════════
# COVER PAGE
# ══════════════════════════════════════════════════════════════
cover = doc.add_paragraph()
cover.alignment = WD_ALIGN_PARAGRAPH.CENTER
cover.paragraph_format.space_before = Pt(60)
styled_run(cover, 'GMinsta', bold=True, size=36, color=(131, 58, 180))

cover2 = doc.add_paragraph()
cover2.alignment = WD_ALIGN_PARAGRAPH.CENTER
styled_run(cover2, 'Mini Social Media Application', bold=False, size=18, color=(100, 100, 100))

doc.add_paragraph()
cover3 = doc.add_paragraph()
cover3.alignment = WD_ALIGN_PARAGRAPH.CENTER
styled_run(cover3, 'End-to-End Software Engineering Report', bold=True, size=14)

doc.add_paragraph()
for line in [
    'Course: Software Development Methodologies (SDM)',
    'Level: 2nd Year Computer Science',
    'Submission Date: April 2026',
]:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    styled_run(p, line, size=12, color=(80, 80, 80))

doc.add_page_break()

# ══════════════════════════════════════════════════════════════
# TABLE OF CONTENTS (manual)
# ══════════════════════════════════════════════════════════════
toc_title = doc.add_paragraph()
styled_run(toc_title, 'TABLE OF CONTENTS', bold=True, size=14, color=(131, 58, 180))
toc_items = [
    ('1', 'Problem Definition & Scope'),
    ('2', 'Requirement Engineering'),
    ('3', 'Feasibility Study'),
    ('4', 'System Design'),
    ('5', 'UML Modeling'),
    ('6', 'System Architecture'),
    ('7', 'Database Design'),
    ('8', 'UI/UX Design'),
    ('9', 'Improvements & Extra Features'),
    ('10', 'Conclusion'),
]
for num, title in toc_items:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    styled_run(p, f'  {num}.  {title}', size=11)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════
# SECTION 1
# ══════════════════════════════════════════════════════════════
heading1('SECTION 1: PROBLEM DEFINITION & SCOPE')
divider()

heading2('1.1 Introduction to GMinsta')
body('In today\'s digital era, social media platforms have become essential for daily communication and content sharing. Platforms such as Instagram, Facebook, and Twitter allow millions of users to connect, share, and interact. However, many of these platforms are large and complex — difficult to study from a developer\'s perspective.')
body('GMinsta (Google Minsta) is a lightweight, feature-rich mini social media application inspired by Instagram. It is designed to demonstrate core software engineering principles by building a real-world application from scratch. GMinsta allows users to register, log in, share image posts, interact through likes and comments, send direct messages, and manage their profiles.')

heading2('1.2 Objectives of the System')
for obj in [
    'User Authentication: Allow users to register and securely log in using username and password.',
    'Content Sharing: Enable users to upload image posts with optional captions.',
    'Social Interaction: Allow users to like and comment on posts.',
    'Follow System: Enable users to follow or unfollow each other to curate their feed.',
    'Messaging: Provide a direct messaging (chat) feature for private communication.',
    'Profile Management: Allow users to edit bio, update profile picture, and view post history.',
    'User Discovery: Enable users to search for and discover other users by username.',
    'Safety Features: Include a block mechanism to allow users to block unwanted interactions.',
    'Notifications: Alert users when someone likes, comments, follows, or messages them.',
    'Dark Mode: Allow users to toggle between light and dark themes.',
]:
    bullet(obj)

heading2('1.3 Scope of the Application')
heading3('In Scope:')
for item in [
    'User registration and login (authentication)',
    'Image uploading and captioning (posts)',
    'Like and comment functionality on posts',
    'User profile with editable bio and profile picture',
    'Follow/unfollow system',
    'Personalized feed (posts from followed users)',
    'Direct messaging between users',
    'User search by username',
    'Block/unblock users',
    'In-app notification system',
    'Dark mode toggle (saved per user)',
    'Explore page (all public posts)',
    'Post deletion (own posts only)',
    'Private account setting',
]:
    bullet(item)

heading3('Out of Scope (Future Work):')
for item in [
    'Real-time WebSocket-based notifications',
    'Video uploads / Stories / Reels',
    'End-to-end encrypted messaging',
    'Third-party OAuth login (Google, Facebook)',
    'Mobile application (Android/iOS)',
]:
    bullet(item)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════
# SECTION 2
# ══════════════════════════════════════════════════════════════
heading1('SECTION 2: REQUIREMENT ENGINEERING')
divider()

heading2('2.1 Stakeholder Identification')
heading3('2.1.1 End Users (Registered Members)')
body('Individuals who create accounts and use GMinsta to post content and interact. They are the primary users of all core features: login, posting, following, messaging, and profile management.')

heading3('2.1.2 System Administrator')
body('Responsible for managing the database, monitoring server health, and handling abuse reports. Needs access to backend infrastructure to maintain system stability and data integrity.')

heading3('2.1.3 Developers')
body('The software engineering team responsible for designing, coding, testing, and deploying the application. Require clear technical specifications, structured code, and proper documentation.')

heading2('2.2 Functional Requirements')
body('Functional Requirements describe what the system must do.')

heading3('Authentication Module')
fr_auth = [
    'FR-01: The system shall allow new users to register with a unique username, valid email, and password.',
    'FR-02: The system shall hash passwords before storing them in the database.',
    'FR-03: The system shall allow registered users to log in using their username and password.',
    'FR-04: The system shall redirect unauthenticated users to the login page.',
    'FR-05: The system shall allow users to log out and invalidate their session.',
]
for f in fr_auth: bullet(f)

heading3('Posts Module')
for f in [
    'FR-06: The system shall allow logged-in users to upload image posts (PNG, JPG, JPEG, GIF, WEBP).',
    'FR-07: The system shall allow users to add a caption (up to 2000 characters) to their posts.',
    'FR-08: The system shall display posts with author username, profile picture, caption, likes, comments, and timestamp.',
    'FR-09: The system shall enforce a maximum file size of 16MB for image uploads.',
    'FR-10: The system shall allow users to delete their own posts.',
]:
    bullet(f)

heading3('Feed & Explore Module')
for f in [
    'FR-11: The system shall display a personalized feed showing posts from followed users.',
    'FR-12: The feed shall be displayed in reverse chronological order (newest first).',
    'FR-13: The system shall exclude posts from blocked users from the feed.',
    'FR-14: The system shall provide an Explore page showing all public posts.',
]:
    bullet(f)

heading3('Likes & Comments Module')
for f in [
    'FR-15: The system shall allow logged-in users to like or unlike any post.',
    'FR-16: The system shall display the total like count per post.',
    'FR-17: The system shall allow logged-in users to add text comments to any post.',
    'FR-18: The system shall display all comments on a post in chronological order.',
]:
    bullet(f)

heading3('Profile Module')
for f in [
    'FR-19: The system shall display a user profile page with username, bio, profile picture, and all posts.',
    'FR-20: The system shall display follower and following counts on the profile.',
    'FR-21: The system shall allow the logged-in user to edit their bio and update their profile picture.',
    'FR-22: The system shall allow users to toggle their account as private.',
]:
    bullet(f)

heading3('Follow, Chat, Search & Safety Modules')
for f in [
    'FR-23: The system shall allow users to follow or unfollow other users.',
    'FR-24: A user shall not be allowed to follow themselves.',
    'FR-25: The system shall allow two registered users to exchange private text messages.',
    'FR-26: The system shall display conversation history in ascending chronological order.',
    'FR-27: The system shall allow users to search for other users by username.',
    'FR-28: The system shall allow users to block other users.',
    'FR-29: Blocking a user shall automatically remove any existing follow relationships.',
    'FR-30: The system shall send in-app notifications for likes, comments, follows, and messages.',
]:
    bullet(f)

heading2('2.3 Non-Functional Requirements')

heading3('Performance')
for f in [
    'Pages shall load within 2 seconds under normal network conditions.',
    'The feed shall efficiently handle at least 500 posts without slowdown.',
    'Images shall be served from a static directory for fast retrieval.',
]:
    bullet(f)

heading3('Security')
for f in [
    'Passwords must be stored as hashed values using Werkzeug\'s generate_password_hash.',
    'Session tokens must be server-side managed using Flask\'s signed session cookies.',
    'File uploads must be validated for type and size to prevent malicious file injection.',
    'Uploaded filenames must be sanitized and randomized with a hex token.',
]:
    bullet(f)

heading3('Usability')
for f in [
    'The interface shall be intuitive and responsive, following social media conventions.',
    'Flash messages shall be displayed for all user actions (success, error, warning).',
    'The navigation bar shall always be visible for easy access to core features.',
    'The application shall be mobile-friendly using Bootstrap\'s responsive grid.',
]:
    bullet(f)

heading3('Maintainability & Scalability')
for f in [
    'The codebase shall follow modular design separating concerns: models, routes, templates, static.',
    'All database models shall be defined using SQLAlchemy ORM for portability.',
    'Configuration shall be externalized in environment variables.',
    'The database shall support indexing on frequently queried fields.',
]:
    bullet(f)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════
# SECTION 3
# ══════════════════════════════════════════════════════════════
heading1('SECTION 3: FEASIBILITY STUDY')
divider()

heading2('3.1 Technical Feasibility — FEASIBLE')
body('All required technologies are open-source, freely available, and well-documented:')
for f in [
    'Python: Mature, widely supported, beginner-friendly.',
    'Flask: Lightweight web framework with extensive documentation.',
    'MySQL: Robust, free, open-source relational database.',
    'SQLAlchemy: Powerful ORM reducing SQL injection risk.',
    'Bootstrap 5: Responsive CSS framework reducing custom styling effort.',
    'Hosting: Can run locally or deploy to PythonAnywhere, Heroku, or AWS.',
]:
    bullet(f)

heading2('3.2 Economic Feasibility — FEASIBLE')
add_table(
    ['Item', 'Cost'],
    [
        ['Python, Flask, SQLAlchemy', 'Free / Open Source'],
        ['MySQL Community Edition', 'Free'],
        ['Bootstrap 5, FontAwesome', 'Free / CDN'],
        ['Development Hardware', 'Existing student laptops'],
        ['Local Hosting (development)', 'Free'],
        ['Domain Name (optional)', '~$10–$15/year'],
        ['Total Estimated Cost', '~$0 – $15'],
    ]
)

heading2('3.3 Operational Feasibility — FEASIBLE')
for f in [
    'Easy to install with a requirements.txt file — one pip install command.',
    'Database schema auto-generated by SQLAlchemy\'s db.create_all().',
    'Familiar Instagram-like UI — users find it immediately intuitive.',
    'Maintainable by a single developer or small team with basic Python knowledge.',
    'Clear README documentation ensures reproducibility across environments.',
]:
    bullet(f)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════
# SECTION 4
# ══════════════════════════════════════════════════════════════
heading1('SECTION 4: SYSTEM DESIGN')
divider()

heading2('4.1 Overview')
body('GMinsta follows a structured, modular design approach to separate concerns and improve maintainability. The design principles followed include: Separation of Concerns, Don\'t Repeat Yourself (DRY), and Single Responsibility Principle.')

heading2('4.2 Modular Design')
modules = [
    ('Module 1: Authentication', 'Handles registration, login, logout, session management.', '/register, /login, /logout'),
    ('Module 2: Posts', 'Manages creation, display, liking, commenting, deletion.', '/post/create, /post/like/<id>, /post/comment/<id>, /post/delete/<id>'),
    ('Module 3: Feed & Explore', 'Assembles personalized feed and public explore page.', '/ (feed), /explore'),
    ('Module 4: Profile', 'Displays and edits profiles, manages follow/block actions.', '/profile/<username>, /profile/edit, /follow/<username>, /block/<username>'),
    ('Module 5: Chat', 'Handles private direct messaging between users.', '/chat, /chat/<username>'),
    ('Module 6: Search', 'Enables user discovery by username.', '/search'),
    ('Module 7: Notifications', 'Tracks and displays in-app notifications.', '/notifications, /notifications/count'),
]
add_table(['Module', 'Responsibility', 'Routes'], modules)

heading2('4.3 Data Flow — Example: Liking a Post')
steps = [
    ('1', 'User clicks the heart icon on a post in the Feed page.'),
    ('2', 'Browser submits a POST request to /post/like/<post_id>.'),
    ('3', 'Flask route handler (like_post) receives the request.'),
    ('4', '@login_required decorator verifies the user is authenticated.'),
    ('5', 'SQLAlchemy queries the Like table to check for existing like.'),
    ('6', 'If already liked → DELETE the Like record. If not → INSERT new Like.'),
    ('7', 'A Notification record is created for the post author.'),
    ('8', 'db.session.commit() saves all changes to MySQL.'),
    ('9', 'User is redirected back; feed re-renders with updated like state.'),
]
for num, step in steps:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Cm(0.5)
    styled_run(p, f'Step {num}: ', bold=True, size=11)
    styled_run(p, step, size=11)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════
# SECTION 5
# ══════════════════════════════════════════════════════════════
heading1('SECTION 5: UML MODELING')
divider()

heading2('5.1 Use Case Diagram')
body('The Use Case Diagram models interactions between Actors and Use Cases (system functions).')
heading3('Actors:')
for a in [
    'Guest (Unauthenticated User): Can register and log in only.',
    'Registered User (Member): Can access all core application features.',
    'System Administrator: Can manage the database and monitor the server.',
]:
    bullet(a)

heading3('Use Case Table:')
add_table(
    ['Use Case', 'Guest', 'Member', 'Admin'],
    [
        ['Register Account', '✓', '—', '—'],
        ['Log In / Log Out', '✓', '✓', '—'],
        ['View/Browse Feed', '—', '✓', '—'],
        ['Create Post', '—', '✓', '—'],
        ['Like / Unlike Post', '—', '✓', '—'],
        ['Comment on Post', '—', '✓', '—'],
        ['View User Profile', '—', '✓', '—'],
        ['Edit Own Profile', '—', '✓', '—'],
        ['Follow / Unfollow User', '—', '✓', '—'],
        ['Block / Unblock User', '—', '✓', '—'],
        ['Send Direct Message', '—', '✓', '—'],
        ['Search for Users', '—', '✓', '—'],
        ['View Notifications', '—', '✓', '—'],
        ['Toggle Dark Mode', '—', '✓', '—'],
        ['Explore Public Posts', '—', '✓', '—'],
        ['Manage Database', '—', '—', '✓'],
    ]
)

heading2('5.2 Class Diagram')
body('The Class Diagram models the data structure — entities (classes), their attributes, and relationships.')

classes = [
    ('User', 'id (PK), username, email, password_hash, profile_pic, bio, is_private, dark_mode, created_at', 'is_following(), follow(), unfollow(), followers_count(), following_count(), unread_notifications()'),
    ('Post', 'id (PK), user_id (FK), image, caption, created_at', 'is_liked_by(user_id), like_count()'),
    ('Comment', 'id (PK), user_id (FK), post_id (FK), text, created_at', '—'),
    ('Like', 'id (PK), user_id (FK), post_id (FK)', '—'),
    ('Message', 'id (PK), sender_id (FK), receiver_id (FK), message, timestamp, is_read', '—'),
    ('Block', 'id (PK), blocker_id (FK), blocked_id (FK)', '—'),
    ('Notification', 'id (PK), recipient_id (FK), actor_id (FK), notif_type, post_id (FK), is_read, created_at', '—'),
    ('followers (Table)', 'follower_id (FK), following_id (FK)', 'Many-to-Many association'),
]
add_table(['Class', 'Attributes', 'Methods / Notes'], classes)

heading3('Relationships:')
for r in [
    'User → Post: One-to-Many (a user can have many posts)',
    'User → Comment: One-to-Many (a user can write many comments)',
    'User → Like: One-to-Many (a user can like many posts)',
    'Post → Comment: One-to-Many (a post can have many comments)',
    'Post → Like: One-to-Many (a post can have many likes)',
    'User ↔ User (via followers table): Many-to-Many (self-referential following)',
    'User → Message: One-to-Many as Sender; One-to-Many as Receiver',
    'User → Notification: One-to-Many (many notifications per user)',
]:
    bullet(r)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════
# SECTION 6
# ══════════════════════════════════════════════════════════════
heading1('SECTION 6: SYSTEM ARCHITECTURE')
divider()

heading2('6.1 3-Tier Architecture')

tiers = [
    ('Tier 1 – Presentation Layer', 'HTML5, CSS3, Bootstrap 5, Jinja2, FontAwesome', 'Renders the user interface. Jinja2 templates inject Python variables into HTML. base.html provides a consistent layout inherited by all pages.'),
    ('Tier 2 – Application Layer', 'Python 3, Flask Framework, Werkzeug', 'Houses all business logic. Handles HTTP routing, session management, authentication, form processing, and file uploads via SQLAlchemy ORM.'),
    ('Tier 3 – Data Layer', 'MySQL, SQLAlchemy ORM, PyMySQL', 'Stores all persistent data: users, posts, comments, likes, messages, follows, blocks, notifications. Enforces integrity via foreign keys and unique constraints.'),
]
add_table(['Tier', 'Technologies', 'Description'], tiers)

heading2('6.2 Technology Stack')
add_table(
    ['Layer', 'Technology', 'Purpose'],
    [
        ['Frontend', 'HTML5, Bootstrap 5, Jinja2', 'UI structure and responsive layout'],
        ['CSS', 'Custom CSS + Bootstrap', 'Styling, dark mode, animations'],
        ['Icons', 'FontAwesome 6', 'Visual icons in UI'],
        ['Fonts', 'Google Fonts (Inter, Dancing Script)', 'Modern typography'],
        ['Backend', 'Python 3, Flask', 'Server-side logic and routing'],
        ['ORM', 'Flask-SQLAlchemy', 'Database abstraction layer'],
        ['Database', 'MySQL', 'Relational data storage'],
        ['DB Driver', 'PyMySQL', 'Python ↔ MySQL connector'],
        ['Security', 'Werkzeug', 'Password hashing and file utilities'],
        ['Sessions', 'Flask Sessions', 'User authentication state'],
    ]
)

heading2('6.3 Component Interaction — Create Post Flow')
steps2 = [
    ('1', 'User navigates to /post/create in the browser.'),
    ('2', 'Flask Router maps this URL to the create_post() function.'),
    ('3', '@login_required decorator checks the session for user_id.'),
    ('4', 'Flask renders create_post.html using Jinja2.'),
    ('5', 'User selects image (drag-and-drop), writes caption, clicks Submit.'),
    ('6', 'Browser sends POST multipart/form-data request to /post/create.'),
    ('7', 'Werkzeug validates and sanitizes the filename.'),
    ('8', 'File saved to static/uploads/posts/ with a unique hex token prefix.'),
    ('9', 'New Post ORM object added to SQLAlchemy session.'),
    ('10', 'db.session.commit() triggers INSERT SQL into MySQL posts table.'),
    ('11', 'Flask redirects to feed; feed re-renders with the new post.'),
]
for num, step in steps2:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Cm(0.5)
    styled_run(p, f'Step {num}: ', bold=True, size=11)
    styled_run(p, step, size=11)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════
# SECTION 7
# ══════════════════════════════════════════════════════════════
heading1('SECTION 7: DATABASE DESIGN')
divider()

heading2('7.1 ER Diagram — Entity Relationships')
body('The following relationships exist between database entities:')
for r in [
    'USERS is the central entity — relates to almost every other entity.',
    'A USER can create many POSTS (1:Many).',
    'A USER can write many COMMENTS (1:Many).',
    'A USER can create many LIKES (1:Many).',
    'A POST can have many COMMENTS and many LIKES (1:Many each).',
    'A USER can send and receive many MESSAGES (Many:Many via sender_id/receiver_id).',
    'USERS follow each other via the FOLLOWERS association table (Many:Many self-referential).',
    'A USER can block other USERS via the BLOCKS table.',
    'A USER receives many NOTIFICATIONS (1:Many).',
]:
    bullet(r)

heading2('7.2 Database Tables')

heading3('Table 1: users')
add_table(
    ['Column', 'Data Type', 'Constraints', 'Description'],
    [
        ['id', 'INTEGER', 'PK, AUTO_INCREMENT', 'Unique user identifier'],
        ['username', 'VARCHAR(50)', 'NOT NULL, UNIQUE', "User's unique handle"],
        ['email', 'VARCHAR(120)', 'NOT NULL, UNIQUE', "User's email address"],
        ['password_hash', 'VARCHAR(256)', 'NOT NULL', 'Hashed password'],
        ['profile_pic', 'VARCHAR(200)', "DEFAULT 'default.jpg'", 'Profile picture filename'],
        ['bio', 'VARCHAR(500)', "DEFAULT ''", "User's biography text"],
        ['is_private', 'BOOLEAN', 'DEFAULT FALSE', 'Private account flag'],
        ['dark_mode', 'BOOLEAN', 'DEFAULT FALSE', 'Dark mode preference'],
        ['created_at', 'DATETIME', 'DEFAULT NOW()', 'Registration timestamp'],
    ]
)

heading3('Table 2: posts')
add_table(
    ['Column', 'Data Type', 'Constraints', 'Description'],
    [
        ['id', 'INTEGER', 'PK, AUTO_INCREMENT', 'Unique post identifier'],
        ['user_id', 'INTEGER', 'NOT NULL, FK → users.id', 'Author of the post'],
        ['image', 'VARCHAR(200)', 'NOT NULL', 'Filename of uploaded image'],
        ['caption', 'VARCHAR(2000)', "DEFAULT ''", 'Optional text caption'],
        ['created_at', 'DATETIME', 'DEFAULT NOW()', 'Post creation timestamp'],
    ]
)

heading3('Table 3: comments')
add_table(
    ['Column', 'Data Type', 'Constraints', 'Description'],
    [
        ['id', 'INTEGER', 'PK, AUTO_INCREMENT', 'Unique comment identifier'],
        ['user_id', 'INTEGER', 'NOT NULL, FK → users.id', 'Author of the comment'],
        ['post_id', 'INTEGER', 'NOT NULL, FK → posts.id', 'Associated post'],
        ['text', 'VARCHAR(500)', 'NOT NULL', 'Comment text content'],
        ['created_at', 'DATETIME', 'DEFAULT NOW()', 'Comment timestamp'],
    ]
)

heading3('Table 4: likes')
add_table(
    ['Column', 'Data Type', 'Constraints', 'Description'],
    [
        ['id', 'INTEGER', 'PK, AUTO_INCREMENT', 'Unique like identifier'],
        ['user_id', 'INTEGER', 'NOT NULL, FK → users.id', 'User who liked the post'],
        ['post_id', 'INTEGER', 'NOT NULL, FK → posts.id', 'Post that was liked'],
    ]
)

heading3('Table 5: messages')
add_table(
    ['Column', 'Data Type', 'Constraints', 'Description'],
    [
        ['id', 'INTEGER', 'PK, AUTO_INCREMENT', 'Unique message identifier'],
        ['sender_id', 'INTEGER', 'NOT NULL, FK → users.id', 'User who sent the message'],
        ['receiver_id', 'INTEGER', 'NOT NULL, FK → users.id', 'User who received the message'],
        ['message', 'VARCHAR(2000)', 'NOT NULL', 'Text content of the message'],
        ['timestamp', 'DATETIME', 'DEFAULT NOW()', 'Time message was sent'],
        ['is_read', 'BOOLEAN', 'DEFAULT FALSE', 'Whether message was read'],
    ]
)

heading3('Table 6: followers (Association Table)')
add_table(
    ['Column', 'Data Type', 'Constraints', 'Description'],
    [
        ['follower_id', 'INTEGER', 'FK → users.id', 'The user doing the following'],
        ['following_id', 'INTEGER', 'FK → users.id', 'The user being followed'],
    ]
)

heading3('Table 7: blocks')
add_table(
    ['Column', 'Data Type', 'Constraints', 'Description'],
    [
        ['id', 'INTEGER', 'PK, AUTO_INCREMENT', 'Unique block record identifier'],
        ['blocker_id', 'INTEGER', 'NOT NULL, FK → users.id', 'User who initiated the block'],
        ['blocked_id', 'INTEGER', 'NOT NULL, FK → users.id', 'User who is blocked'],
    ]
)

heading3('Table 8: notifications')
add_table(
    ['Column', 'Data Type', 'Constraints', 'Description'],
    [
        ['id', 'INTEGER', 'PK, AUTO_INCREMENT', 'Unique notification identifier'],
        ['recipient_id', 'INTEGER', 'NOT NULL, FK → users.id', 'User receiving the notification'],
        ['actor_id', 'INTEGER', 'NOT NULL, FK → users.id', 'User who triggered the notification'],
        ['notif_type', 'VARCHAR(20)', 'NOT NULL', 'Type: like, comment, follow, message'],
        ['post_id', 'INTEGER', 'FK → posts.id, NULLABLE', 'Related post (if applicable)'],
        ['is_read', 'BOOLEAN', 'DEFAULT FALSE', 'Whether notification was read'],
        ['created_at', 'DATETIME', 'DEFAULT NOW()', 'Notification timestamp'],
    ]
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════
# SECTION 8
# ══════════════════════════════════════════════════════════════
heading1('SECTION 8: UI/UX DESIGN')
divider()

heading2('8.1 Design Principles')
for p_text in [
    'Familiarity: UI mirrors Instagram so users require no learning curve.',
    'Minimalism: Clean backgrounds, card-based posts, minimal clutter.',
    'Consistency: Uniform Inter font, Bootstrap components, and gradient color palette throughout.',
    'Feedback: Immediate flash messages after every user action.',
    'Responsiveness: Bootstrap\'s grid ensures the layout adapts to all screen sizes.',
    'Dark Mode: Full dark mode support with CSS variables, toggled per user.',
]:
    bullet(p_text)

heading2('8.2 Screen Descriptions')

screens = [
    ('Login (/login)', 'Centered card with gradient GMinsta logo, username/password input fields, gradient Log In button, and "Sign up" link below.'),
    ('Register (/register)', 'Centered card with email, username, and password fields. Gradient Sign Up button with terms notice below.'),
    ('Feed (/)', 'Fixed navbar with icons. Centered single-column post cards. Each card: author avatar + username, post image, like/comment/message actions, likes count, caption, comments list, comment input box.'),
    ('Profile (/profile/<username>)', 'Large circular avatar, username, stats (posts/followers/following), bio, Follow/Message/Block buttons. 3-column grid of post thumbnails with like/comment overlay on hover.'),
    ('Chat (/chat/<username>)', 'Chat header with avatar. Scrollable message history with gradient sent bubbles (right) and grey received bubbles (left). Timestamps below each. Input bar at bottom.'),
    ('Search (/search)', 'Search bar with magnifying glass icon. Results as user cards with avatar, username, follower count, and Follow button.'),
    ('Notifications (/notifications)', 'List of notification items: actor avatar, description text (liked/commented/followed/messaged), timestamp, post thumbnail, and Follow Back button for follows.'),
    ('Explore (/explore)', '3-column grid of all public posts with like/comment count overlay on hover.'),
    ('Create Post (/post/create)', 'Drag-and-drop upload zone with live image preview. Caption textarea. Share Post button.'),
    ('Edit Profile (/profile/edit)', 'Live avatar preview with Change Photo button. Bio textarea. Private account toggle. Save Changes button.'),
]
add_table(['Screen', 'Description'], screens)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════
# SECTION 9
# ══════════════════════════════════════════════════════════════
heading1('SECTION 9: IMPROVEMENTS & EXTRA FEATURES')
divider()

heading2('9.1 Notifications System (Implemented)')
body('GMinsta includes a full in-app notification system that alerts users when:')
for item in [
    'Someone likes their post.',
    'Someone comments on their post.',
    'A new user follows them.',
    'They receive a new direct message.',
]:
    bullet(item)
body('Implementation: A Notification table stores recipient_id, actor_id, notif_type, post_id, is_read, and created_at. A red badge on the navbar heart icon shows unread count. All notifications marked as read when the page is visited.')

heading2('9.2 Privacy Settings (Implemented)')
body('Users can set their account to Private mode from the Edit Profile page. The is_private boolean field is stored in the users table. Private account label displays on their profile for non-followers.')

heading2('9.3 Dark Mode (Implemented)')
body('Full dark mode implemented using CSS custom properties (--bg, --card-bg, --text, --border, etc.). The dark_mode boolean is stored per-user in the database. Toggle button (moon/sun icon) in the navbar applies the change immediately and persists across sessions.')

heading2('9.4 Security Enhancements')
add_table(
    ['Enhancement', 'Implementation'],
    [
        ['Password Hashing', 'Werkzeug generate_password_hash / check_password_hash'],
        ['Session Management', 'Flask signed session cookies with secret key'],
        ['File Upload Validation', 'Extension whitelist + secure_filename + hex token prefix'],
        ['SQL Injection Prevention', 'SQLAlchemy ORM (parameterized queries — no raw SQL)'],
        ['CSRF Awareness', 'All mutations use POST requests only'],
        ['Min Password Length', '6-character minimum enforced on registration'],
        ['Block System', 'Comprehensive user blocking removing follows in both directions'],
        ['Future: CSRF Tokens', 'Flask-WTF integration recommended for production'],
        ['Future: Rate Limiting', 'Flask-Limiter to prevent brute-force login attacks'],
        ['Future: HTTPS/SSL', 'Deploy behind Nginx with Let\'s Encrypt certificate'],
    ]
)

heading2('9.5 Additional Future Features')
for f in [
    'Hashtag Support: Allow posts to include clickable hashtags.',
    'Post Likes from Explore: Like posts directly from the Explore grid.',
    'Username Tagging: Tag other users in captions/comments with @username.',
    'Real-time Chat: WebSocket-based messaging using Flask-SocketIO.',
    'Two-Factor Authentication (2FA): OTP to email on login.',
    'Story Feature: 24-hour temporary posts visible to followers only.',
    'Image Filters: Apply CSS filters before posting.',
    'Video Uploads: Support MP4 video posts.',
]:
    bullet(f)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════
# SECTION 10
# ══════════════════════════════════════════════════════════════
heading1('SECTION 10: CONCLUSION')
divider()

heading2('10.1 Summary of the System')
body('GMinsta is a fully functional mini social media application built using modern software engineering principles and a carefully chosen technology stack. The system successfully implements all core social media features:')
for f in [
    'Secure User Authentication with hashed passwords and session management.',
    'Image Post Creation with drag-and-drop upload, captions, and deletion.',
    'Like & Comment System with real-time feedback.',
    'Follow/Unfollow System curating a personalized feed.',
    'Explore Page for discovering all public posts.',
    'Direct Messaging with conversation history and read receipts.',
    'User Profile with 3-column grid, stats, bio, and private mode.',
    'In-App Notification System for likes, comments, follows, and messages.',
    'Dark Mode per user, stored in the database.',
    'Block / Unblock safety system.',
    'User Search with partial matching.',
]:
    bullet(f)

body('The project was developed following a complete SDLC: Problem Definition → Requirements → Feasibility → Design → UML → Database → Implementation.')

heading2('10.2 Importance of Software Engineering in Real-World Applications')
body('This project illustrates several fundamental software engineering principles:')
for point in [
    'Structured Methodology: Using SDLC phases prevented ad-hoc coding and reduced defects.',
    'Modular Architecture: Separating modules made the codebase easier to develop, test, and extend.',
    'Security-First Design: Password hashing, session management, and input validation from the start.',
    'Database Design: Normalized relational schema prevents redundancy and maintains integrity.',
    'User-Centred Design: UI/UX decisions ensure the application meets real user needs.',
    'Scalability & Maintainability: ORM, externalized config, and DRY principles enable growth.',
]:
    bullet(point)

body('In conclusion, GMinsta demonstrates that disciplined software engineering — from requirements gathering through design, implementation, and future improvement planning — is the foundation of reliable, secure, and scalable software systems.')

divider()

heading2('References')
refs = [
    'Sommerville, I. (2016). Software Engineering (10th ed.). Pearson Education.',
    'Flask Documentation. (2024). https://flask.palletsprojects.com/',
    'SQLAlchemy Documentation. (2024). https://docs.sqlalchemy.org/',
    'Bootstrap 5 Documentation. (2024). https://getbootstrap.com/docs/5.3/',
    'OWASP Top Ten. (2021). Web Application Security Risks. https://owasp.org/',
    'MySQL Documentation. (2024). https://dev.mysql.com/doc/',
]
for i, ref in enumerate(refs, 1):
    bullet(f'[{i}] {ref}')

# ══════════════════════════════════════════════════════════════
# SAVE
# ══════════════════════════════════════════════════════════════
output_path = os.path.join(os.path.dirname(__file__), 'GMinsta_Report.docx')
doc.save(output_path)
print('\nReport saved successfully!\nFile: ' + output_path + '\n')
