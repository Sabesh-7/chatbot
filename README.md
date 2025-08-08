# College Assistant Chatbot

A Streamlit-based chatbot application for college information management with secure authentication and vector search capabilities using MongoDB Cloud Atlas.

## 🚀 Features

- **Secure Authentication**: MongoDB Cloud Atlas with bcrypt password hashing
- **User Registration**: Self-registration for students and staff
- **Role-based Access**: Admin, Staff, and Student roles with different permissions
- **Vector Search**: Pinecone integration for semantic document search
- **Chat Interface**: Interactive chat with college information
- **Admin Panel**: Add and manage college information
- **Modern UI**: Clean and responsive Streamlit interface

## 📁 Project Structure

```
Chatbot/
├── main.py                 # Main application entry point
├── config.py              # Application configuration
├── requirements.txt       # Python dependencies
├── connect_to_cloud_atlas.py  # Cloud Atlas connection script
├── logging_config.py     # Logging configuration
├── src/                 # Source code
│   ├── database/        # MongoDB models and authentication
│   │   ├── models.py    # MongoDB User model and connection
│   │   └── auth.py      # Authentication functions
│   ├── chatbot/         # Chatbot with Pinecone integration
│   │   └── college_chatbot.py
│   └── ui/              # Streamlit UI components
│       └── interfaces.py
└── venv/                # Virtual environment
```

## 🛠️ Prerequisites

- Python 3.8+
- MongoDB Cloud Atlas account
- Pinecone account and API key (optional, for vector search)

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MongoDB Cloud Atlas**
   - Create a free account at [MongoDB Cloud Atlas](https://www.mongodb.com/cloud/atlas)
   - Create a new cluster (FREE tier)
   - Set up database user and network access
   - Get your connection string

5. **Connect to Cloud Atlas**
   ```bash
   python connect_to_cloud_atlas.py
   ```

6. **Run the application**
   ```bash
   streamlit run main.py
   ```

## 🔐 Default Credentials

- **Admin**: username: `admin`, password: `admin123`
- **New users**: Register through the application interface

## 🎯 Usage

### For Students/Staff
1. Register a new account or login with existing credentials
2. Use the chat interface to ask questions about college information
3. Use quick action buttons for common queries

### For Admins
1. Login with admin credentials
2. Add college information through the admin panel
3. Manage user accounts and reset passwords
4. View user list and analytics

## 🗄️ MongoDB Cloud Atlas Setup

### Quick Setup Guide

1. **Create MongoDB Cloud Atlas Account**
   - Go to [MongoDB Cloud Atlas](https://www.mongodb.com/cloud/atlas)
   - Sign up for a free account

2. **Create a Cluster**
   - Click "Build a Database"
   - Choose "FREE" tier (M0)
   - Select your preferred cloud provider and region
   - Click "Create"

3. **Set Up Database Access**
   - Go to "Database Access" in the left sidebar
   - Click "Add New Database User"
   - Create a username and password
   - Select "Read and write to any database"
   - Click "Add User"

4. **Set Up Network Access**
   - Go to "Network Access" in the left sidebar
   - Click "Add IP Address"
   - Click "Allow Access from Anywhere" (for development)
   - Click "Confirm"

5. **Get Connection String**
   - Go to "Database" in the left sidebar
   - Click "Connect"
   - Choose "Connect your application"
   - Copy the connection string

6. **Connect Your Application**
   ```bash
   python connect_to_cloud_atlas.py
   ```

## 🔧 Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_URI` | - | MongoDB Cloud Atlas connection string |
| `MONGODB_DATABASE` | `college_chatbot` | Database name |
| `MONGODB_COLLECTION` | `users` | Collection name for users |
| `PINECONE_API_KEY` | - | Pinecone API key for vector search |
| `DEBUG` | `True` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |

## 🚨 Troubleshooting

### MongoDB Connection Issues
- Verify your connection string is correct
- Check if your IP address is whitelisted in MongoDB Cloud Atlas
- Ensure your database user has the correct permissions
- Check if your cluster is running

### Authentication Issues
- Verify database connection is working
- Check if user exists in database
- Ensure password requirements (minimum 6 characters)

### Pinecone Issues
- Verify API key is correct in `.env` file
- Check internet connection
- Ensure Pinecone index exists (will be created automatically)

### Import Errors
- Ensure you're in the correct directory
- Check if virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`

## 📝 Logging

- **Location**: `logs/` directory
- **Format**: Daily log files (e.g., `app_20241201.log`)
- **Level**: Configurable via `LOG_LEVEL` in `.env`
- **Console**: Real-time logging during development

## 🔒 Security Features

- **Password Hashing**: All passwords hashed with bcrypt
- **Session Management**: Secure session handling with Streamlit
- **Input Validation**: Form validation and sanitization
- **Role-based Access**: Different interfaces based on user role
- **MongoDB Security**: Connection string authentication and network access controls

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:
1. Check the logs in `logs/` directory
2. Verify your configuration in `.env` file
3. Ensure all dependencies are installed
4. Create an issue with detailed error information
