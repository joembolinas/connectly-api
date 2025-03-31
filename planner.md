# **Homework 5: Adding User Interactions (Likes and Comments)**

For this task, you will expand the Connectly API by adding functionality for user interactions: **likes** and **comments** on posts. You will plan, implement, and test these features, using the diagrams and foundational knowledge from the previous phase as a guide.

* **NOTE** : You can choose to start independently or collaboratively, depending on your schedule and project timeline. Select the method that best fits your needs, but keep in mind that your final output should reflect a unified team decision. Make sure to adjust your project plan accordingly to reflect your chosen approach.*

**Instructions:**

1. **Study Updated Diagrams:**
   1. Open the latest versions of the following diagrams from the previous phase:
      1. **Data Relationship Diagram** : Review how users and posts are currently related.
   2. **CRUD Interaction Flow Diagram** : Analyze how CRUD operations flow for existing endpoints.
   3. Plan how to add likes and comments:
   4. **Relationships** : Determine how likes and comments will link users and posts.
   5. **CRUD Operations** : Identify new endpoints required for liking and commenting.
2. **Refer to These Topics:**
   1. **Relationships in Django Models:**
      1. **Reference** : Relationships Between Data Entities.
      2. Understand **ForeignKey** relationships for associating likes and comments with posts and users.
   2. **Validation in APIs:**
      1. **Reference** : Validation in Django.
      2. Apply validation to ensure input for likes and comments meets defined criteria (e.g., content for comments is not empty).
3. **Update Diagrams:**
   1. Modify the **Data Relationship Diagram** to include relationships for likes and comments.
   2. Update the **CRUD Interaction Flow Diagram** to include new endpoints for these interactions.
4. **Implement Changes:**
   1. Add models:
      1. **Likes** : Reference User and Post.
      2. **Comments** : Reference User, Post, and include content and timestamp.
   2. Create endpoints:
      1. **POST /posts/{id}/like** : Allows users to like a post.
      2. **POST /posts/{id}/comment** : Allows users to comment on a post.
      3. **GET /posts/{id}/comments** : Retrieves all comments for a post.
5. **Advanced Tasks (Optional)**
   1. **Like/Comment Counts:**
      1. Modify the endpoint **GET /posts/{id}** to include:
         1. like_count: The number of likes for the post.
         2. comment_count: The number of comments for the post.
   2. **Pagination for Comments:**
      1. Implement pagination for the **GET /posts/{id}/comments** endpoint to handle large datasets efficiently.

**Test Your API**

1. Use **Postman** to test all endpoints:
2. Validate that likes and comments are saved correctly in the database.
3. Ensure proper error handling for invalid requests (e.g., liking a non-existent post).
4. Test  such as:
   [edge cases](https://airfocus.com/glossary/what-is-an-edge-case/)
5. Liking a post multiple times.
6. Adding a comment to a post that doesn’t exist.
7. Document sample requests and responses, including:
8. A successful request/response.
9. An example of an error response (e.g., 404 Not Found).

**Key Reminders**

1. Focus on Minimum Requirements: Completing the core tasks ensures progress.
2. Optional Features: Advanced tasks allow you to stretch your skills but are not mandatory.
3. Refer to Foundational Knowledge: Use materials from the previous phase to guide your decisions.

# **Homework 6: Integrating Third-Party Services**

For this task, you will integrate **Google OAuth** login into the Connectly API to allow users to log in with their Google accounts. You will plan, implement, and test this functionality while ensuring compatibility with the existing API.

* **NOTE** : You can choose to start independently or collaboratively, depending on your schedule and project timeline. Select the method that best fits your needs, but keep in mind that your final output should reflect a unified team decision. Make sure to adjust your project plan accordingly to reflect your chosen approach.*

**Instructions:**

1. **Study Updated Diagrams:**
   1. Open the latest version of the Authentication and Authorization Flow Diagram.
   2. Review how the current authentication flow manages token validation.
   3. Plan how Google OAuth will integrate:
      1. How will tokens from Google be validated by the API?
      2. How will Google accounts link to existing user profiles?
2. **Refer to These Topics:**
   1. **Authentication Basics:**
      1. **Reference** : Fundamentals of API Security.
      2. Review token-based authentication and its implementation in Django REST Framework.
   2. **External API Integration:**
      1. **Reference** : System Integration.
      2. Understand how APIs interact with external systems (e.g., Google OAuth).
3. **Update Diagrams:**
   1. Modify the **Authentication and Authorization Flow Diagram** to:
      1. Include steps for Google OAuth login.
      2. Represent the linking of Google tokens to user profiles.
4. **Implement Changes:**
   1. **Integrate Google OAuth:**
      1. Use a library such as django-allauth to handle Google login flows.
   2. **Create or Update Endpoints:**
      1. Add or modify the endpoint POST /auth/google/login to handle the login process.
5. **Advanced Tasks (Optional):**
   1. **Error Handling** : Add robust error handling for scenarios like expired tokens or duplicate accounts.
   2. **Profile Pictures** : Allow users to upload profile pictures using a cloud storage service (e.g., Cloudinary).
6. **Test Your API:**
   1. Test the Google OAuth flow:
      1. Log in with a test Google account.
      2. Validate error handling for invalid or expired tokens.
   2. Document successful and error cases with sample requests and responses.

# **Homework 7: Building a News Feed**

In this task, you will expand the Connectly API by adding a **news feed** endpoint to display user-specific content. You will implement sorting and pagination to efficiently retrieve and display posts.

* **NOTE** : You can choose to start independently or collaboratively, depending on your schedule and project timeline. Select the method that best fits your needs, but keep in mind that your final output should reflect a unified team decision. Make sure to adjust your project plan accordingly to reflect your chosen approach.*

**Instructions:**

1. **Study Updated Diagrams:**
   1. Open the **latest versions** of the following diagrams:
      1. **CRUD Interaction Flow Diagram** : Review how updated CRUD processes interact with existing endpoints.
      2. **System Architecture Diagram** : Analyze how system components currently interact.
   2. Plan the implementation of the news feed:
   3. What sorting logic is needed to display posts in the desired order (e.g., by date)?
   4. What filters or user-specific logic might improve the feed?
2. **Refer to These Topics:**
   1. **Efficient Data Handling:**
      1. **Reference** : Validation in APIs.
      2. Use Django ORM or SQL queries to sort and filter data for user-specific feeds.
   2. **Pagination:**
      1. **Reference** : CRUD Operations in the API Context.
      2. Apply pagination to limit the number of results returned in each request
3. **Update Diagrams:**
   1. Modify the **CRUD Interaction Flow Diagram** to:
      1. Add the GET /feed endpoint.
   2. Update the **System Architecture Diagram** to show sorting and filtering logic.
4. **Implement Changes:**
   1. Create a GET /feed endpoint:
      1. **Minimum Requirement** : Retrieve posts sorted by date, with pagination to limit the number of results per request.
      2. Use Django ORM or SQL queries to fetch data efficiently.
5. **Advanced Tasks (Optional):**
   1. **Filtering by User Preferences:**
      1. Allow filtering by user-specific logic, such as:
         1. Posts from followed users.
         2. Posts liked by the user.
   2. **Optimizing for Performance:**
   3. Preload related data (e.g., comments or likes) to reduce query overhead.
   4. Cache results for frequently accessed feeds.
6. **Test Your API:**
   1. Validate Your News Feed Endpoint:
      1. Test the news feed endpoint using sample data:
         1. Retrieve posts sorted by date.
         2. Ensure pagination works correctly, returning the right subset of data.
         3. Test filters if implemented (e.g., posts from followed users).
      2. Handle invalid parameters gracefully (e.g., requesting a non-existent page).
   2. Document Your Testing:
      1. Include sample requests and responses, such as:
         1. A successful feed request showing paginated results.
         2. An error response for invalid parameters or filter

# **Milestone 2: Enhancing Functionality – User Features & Integrations**

This task focuses on finalizing and submitting the Connectly API as it currently stands, incorporating all implemented features from Milestone 2. You will ensure that all functionality is complete, properly tested, and documented with updated diagrams. This submission marks a key milestone, but further enhancements and features will be implemented in the Terminal Assessment.

**Instructions:**

1. **Review and Consolidate**
2. **Gather All Work:**
3. Collect all diagrams, updated code, and testing results from Homework 5, 6, and 7.
4. Ensure all team members’ contributions are included in the final output.
5. **Verify Completion:** Use the submission checklist for each homework to ensure all elements are included:
6. **Diagrams** : Updated Data Relationship Diagram, CRUD Interaction Flow Diagram, System Architecture Diagram, and Authentication and Authorization Flow Diagram.
7. **API Codebase** : Functional implementations for likes, comments, Google OAuth, and the news feed.
8. **Testing Evidence** : Include sample requests and responses for all implemented features.
9. **Test the API**
10. **Conduct Final Tests:**
11. Test the API as a cohesive system to ensure:
12. Likes and comments functionality work without errors.
13. Google OAuth login integrates seamlessly with the authentication flow.
14. The news feed endpoint retrieves and paginates posts as expected.
15. Document and resolve any errors or edge cases identified during testing.
16. **Document Results:**
17. Compile a summary of the final testing results.
18. **Ensure Accuracy:**
19. Review all diagrams to confirm they reflect the current state of the API:
20. Data Relationship Diagram: Includes likes, comments, and any new relationships.
21. CRUD Interaction Flow Diagram: Displays all new and updated endpoints.
22. System Architecture Diagram: Shows how all components (e.g., OAuth, feed logic) interact.
23. Authentication and Authorization Flow Diagram: Details Google OAuth integration and token validation.
24. **Polish for Submission:**
25. Refine the diagrams for clarity and accuracy, ensuring they effectively communicate your API’s current design.
26. **Final Documentation**
27. Prepare your submission package by making a copy of this . Navigate to the **Milestone 2** tab, and document and link all outputs in the designated sections as	follows:
    [worksheet](https://docs.google.com/spreadsheets/d/1t-3cSqcInMxFMgjmx6ONT92KJ5AxuK70NKpVq-M5P7k/copy)
28. Diagrams:
29. Include links to all finalized diagrams.
30. API Codebase:
31. Ensure the codebase is clean, well-commented, and committed to your group’s GitHub repository. Provide the repository link.
32. Testing Evidence:
33. Include a Postman collection or equivalent documentation that demonstrates all requests, responses, and edge cases.
34. Team Contributions:
35. Complete the contribution table in your worksheet, detailing the roles and tasks performed by each team member.
36. **Submit Your Work**
37. As this is your Milestone 2 output, all team members should submit the link to their output. Copy the link and paste it here on Camu.
38. **Prepare for Discussion**
39. Be ready to discuss your group’s output during the next synchronous session.
