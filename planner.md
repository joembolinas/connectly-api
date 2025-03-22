## **Project Overview**

**Project Name:** Connectly – A Social Media API Platform

**Course:** Integrative Programming and Technologies (MO-IT152)

**Objective:** To develop a fully integrated and optimized RESTful API system that enables core functionalities of a social media platform, including user authentication, content sharing, interaction features, and security enhancements.

---

## **Core Features and Functionalities**

---

| **Category** | **Feature** | **Description** | **Status** |
| --- | --- | --- | --- |
| **User Management** | User Registration & Authentication | Secure login and registration using OAuth & JWT | ✅ Complete |
|  | Profile Management | Users can update their personal information and privacy settings | ⚠️ Partial |
| **Content Management** | Posting & Editing | Users can create, edit, and delete posts | ✅ Complete |
|  | Media Upload | Support for images and video sharing | ❌ Not Started |
| **User Interaction** | Likes & Comments | Users can like and comment on posts | ✅ Complete |
|  | Friend Requests | Users can connect and follow each other | ✅ Complete |
| **Security** | Role-Based Access Control (RBAC) | Admins, moderators, and regular users have defined permissions | ✅ Complete |
|  | HTTPS & Data Encryption | Ensuring data privacy with SSL/TLS encryption | ✅ Complete |
| **Optimization** | API Performance Optimization | Using caching and pagination to improve response times | ⚠️ Partial |
| **Testing & Documentation** | Test Coverage | Comprehensive test suite for API endpoints | ❌ Not Started |
|  | API Documentation | Swagger/OpenAPI documentation | ❌ Not Started |

## **Project Workflow and Action Plan**

| **Week#** | **Task Type** | **Task Number** | **Task Name** | **Action Items** | **Expected Output** | **Course Alignment** | **Remarks** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1-2 | Homework | 1-2 | Setting Up API & CRUD Operations | Set up Django, implement authentication, create CRUD operations | API setup with authentication & CRUD | API fundamentals, client-server model | Foundation setup |
| 1-2 | Activity | 1 | Setting Up Django and Django REST Framework | Install dependencies, configure Django project | Functional development environment | API setup |  |
| 1-2 | Activity | 2 | Diagram Analysis 1 | Analyze API system diagrams | Documented analysis | System architecture |  |
| 1-2 | Activity | 3 | Building the Connectly API - CRUD Operations | Implement basic CRUD operations | CRUD-enabled API | API fundamentals |  |
| 1-2 | Activity | 4 | Relating Diagrams to the API | Map API endpoints to diagrams | Visualized API architecture | API structure |  |
| 3 | Homework | 3 | Data Validation & Handling | Implement Django Models, Serializers, API Validation | Validated API with secure data handling | Validation, database relationships | Strengthens API security |
| 3 | Activity | 5 | Diagram Analysis 2 | Evaluate API data flow diagrams | Refined system design | Data integrity |  |
| 3 | Activity | 6 | Enhancing the Connectly API with Validation and Relationships | Implement API validation rules and relations | Data validation integrated | Secure data handling |  |
| 3 | Activity | 7 | Relating Diagrams to the Enhanced API | Map validation logic to diagrams | API workflow refined | Enhanced system design |  |
| 4-5 | Milestone | 1 | API Security & Access Control | Implement RBAC, encryption, HTTPS | Secure API with defined access control | Security best practices, encryption | Enhancing API security |
| 4-5 | Homework | 4 | Group Collaboration for API Security Submission | Secure API endpoints, enforce authentication | API security measures implemented | API security, authentication |  |
| 4-5 | Activity | 8 | Diagram Analysis 3 | Security architecture analysis | Security-focused system design | API protection |  |
| 4-5 | Activity | 9 | Enhancing API Security for Connectly | Apply security policies, encryption | Secure API deployment | Secure API implementation |  |
| 4-5 | Activity | 10 | Connecting Diagrams to Enhanced API | Align security layers with API diagrams | Well-documented security measures | API security strategy |  |
| 6-9 | Milestone | 2 | Enhancing Functionality – User Features & Integrations | Develop post creation, media uploads, and interactions | Fully functional social features | API enhancements, user interactions | Expanding API capabilities |
| 6-9 | Homework | 5 | Adding User Interactions (Likes and Comments) | Implement likes and comment features | Interactive API features | Social media engagement |  |
| 6-9 | Homework | 6 | Integrating Third-Party Services | Connect external APIs (Google OAuth) | Secure user authentication | OAuth, API security |  |
| 6-9 | Homework | 7 | Building a News Feed | Develop a user-based news feed | Real-time content updates | API customization |  |
| 10-12 | Terminal Assessment | - | Performance Optimization & Finalization | Optimize database queries, caching, final testing | Scalable, secure API ready for deployment | Optimization, scalability | Finalizing API |
| 10-12 | Homework | 8 | Privacy Settings and Role-Based Access Control | Implement privacy controls and RBAC | User privacy enforcement | Secure user roles |  |
| 10-12 | Homework | 9 | Performance Optimization | Enhance API performance | High-speed API responses | Performance tuning |  |

## **Project Workflow and Action Plan - Current Progress**

| **Task** | **Status** | **Notes** |
| --- | --- | --- |
| Setting Up API & CRUD Operations | ✅ Complete | Django project structure, REST API endpoints, authentication |
| Data Validation & Handling | ✅ Complete | Models, serializers, validation rules implemented |
| API Security & Access Control | ✅ Complete | RBAC, JWT, token-based authentication |
| Enhancing User Features & Integrations | ⚠️ Partial | Core features complete, media uploads pending |
| Performance Optimization & Finalization | ⚠️ In Progress | Pagination and some caching implemented |
| Testing & Documentation | ❌ Not Started | Needs comprehensive testing and API documentation |

## **Next Steps**

1. **Implement Media Upload Support**
   - Add image/video upload functionality to post creation
   - Implement media file storage and serving

2. **Enhance Test Coverage**
   - Create unit tests for models and serializers
   - Add integration tests for API endpoints
   - Test authentication flows

3. **Create API Documentation**
   - Integrate Swagger/OpenAPI
   - Document all endpoints with request/response examples

4. **Improve Admin Interface**
   - Configure Django admin for all models
   - Add custom admin actions and filters

5. **Complete Performance Optimization**
   - Implement full Redis caching solution
   - Add database indexes for common queries
   - Profile and optimize slow queries

6. **Deploy to Production**
   - Configure PostgreSQL database
   - Set up proper HTTPS
   - Configure production settings