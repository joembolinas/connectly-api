
# **Homework 8: Privacy Settings and Role-Based Access Control (RBAC)**

**In this task, you will implement basic ****Privacy Settings** and** Role-Based Access Control (RBAC)** to secure the Connectly API. You will define roles, enforce access restrictions, and allow users to control the visibility of their posts.

**Instructions:**

1. **Study Existing Implementations and Diagrams: **Review the following:
2. **Authentication Flow** **: Refer to your Google OAuth and token-based authentication implementations from your previous task.**
3. **Likes and Comments Endpoints** **: Examine how you validated user actions and linked them to specific posts for insights into role-based access and privacy settings.**
4. **Implement RBAC**
5. **Define User Roles:**
6. **Add roles (e.g., admin, user, guest) to the user model. Use:**
7. **A role field in the user model (e.g., a string or enum).**
8. **Restrict Access:**
9. **Implement role-checking middleware or decorators:**
10. **Example** **: Only admin users can delete posts or comments.**
11. **Implement Privacy Settings**
12. **Add a privacy field to the post model:**
13. **Options: public, private.**
14. **Update the ****GET /posts/{id}** and **GET /feed **endpoints to enforce privacy settings:
15. **Example** **: Only the post owner can view private posts.**
16. **Update Diagrams: **Update the Access Control Flow Diagram to reflect:
17. **Role-checking logic for sensitive operations.**
18. **Privacy settings logic during data retrieval.**
19. **Test Your API**
20. **Use Postman to validate:**
21. **Role-based access control (e.g., restricting post deletion to admin users).**
22. **Privacy enforcement for posts (e.g., ensuring private posts are inaccessible to other users).**
23. **Document successful and failed test cases:**
24. **Successful requests.**
25. **Failed requests due to invalid permissions or privacy settings.**
26. **Edge cases (e.g., unauthorized users attempting to access restricted resources).**


# **Homework 9: Performance Optimization**

**In this task, you will enhance the performance of key API endpoints by implementing pagination and caching. You will focus on optimizing data retrieval for scalability and efficiency.**

**Instructions:**

1. **Study Existing Implementations**
2. **Review the following:**
3. **News Feed Endpoint** **: Refer to your implementation of the news feed and its sorting logic.**
4. **Pagination** **: Examine any existing pagination logic for comments or posts.**
5. **Reference** **: Efficient Data Handling in APIs.**
6. **Optimize API Performance**
7. **Pagination:**
8. **Add or refine pagination for:**
9. **GET /feed** **: Limit the number of posts returned per request.**
10. **Example** **: Use Django’s Paginator class or DRF’s built-in pagination.**
11. **Caching** **:**
12. **Add caching for frequently accessed endpoints:**
13. **Example** **: Cache results for GET /feed using Django’s caching framework or Redis.**
14. **Advanced Task (Optional)**
15. **Query Optimization:**
16. **Use Django ORM methods like select_related or prefetch_related to optimize database queries.**
17. **Example** **: Preload related data for comments or likes to reduce query overhead.**
18. **Update Diagrams**
19. **Update the CRUD Interaction Flow Diagram:**
20. **Reflect changes to data retrieval processes, including pagination and caching.**
21. **Update the System Architecture Diagram:**
22. **Show components or layers added for performance (e.g., caching).**
23. **Test Your API**
24. **Validate Pagination:**
25. **Test paginated responses for large datasets:**
26. **Example: Ensure GET /feed?page=2 retrieves the correct subset of posts.**
27. **Validate Caching:**
28. **Test cache effectiveness using tools like Redis monitoring or logs.**
29. **Trigger a cache miss (e.g., invalidate the cache) and confirm the cache is repopulated.**
30. **Document Testing:**
31. **Include successful responses, cache hit rates, and response time improvements.**



# **Terminal Assessment: Enhancing Security and Scalability**

**For this task, you will finalize and consolidate your API implementation, ensuring all features are complete, tested, and documented. **

**Instructions:**

1. **Review and Consolidate**
2. **Gather All Work:**
3. **Collect diagrams, updated code, and testing results from Tasks 1 and 2.**
4. **Verify that all features (RBAC, privacy settings, caching, pagination) are functional.**
5. **Refine Codebase:**
6. **Clean and comment your code to ensure readability and maintainability.**
7. **Update Diagrams**
8. **Finalize the following diagrams:**
9. **Access Control Flow Diagram: Reflect role-checking and privacy logic.**
10. **CRUD Interaction Flow Diagram: Include performance optimizations.**
11. **System Architecture Diagram: Show the final state of the API.**
12. **Compile Testing Evidence: Include the following:**
13. **Postman requests and responses for all implemented features.**
14. **Edge case tests for RBAC and privacy settings.**
15. **Performance test results, including cache hit rates and paginated responses.**
16. **Final Documentation**
17. **Prepare your submission package by retrieving your group’s copy of the Enhancing Connectly API worksheet, navigating to the Terminal Assessment tab, and documenting and linking all outputs in the designated sections:**
18. **Diagrams:**
19. **Include links to all finalized diagrams.**
20. **API Codebase:**
21. **Ensure the codebase is clean, well-commented, and committed to your group’s GitHub repository. Provide the repository link.**
22. **Testing Evidence:**
23. **Include a Postman collection or equivalent documentation that demonstrates all requests, responses, and edge cases.**
24. **Team Contributions:**
25. **Complete the contribution table in your worksheet, detailing the roles and tasks performed by each team member.**
26. **Submit Your Work**
27. **As this is your Terminal Assessment output, all team members should submit the link to their output. Copy the link and paste it here on Camu.**
