# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML design had 4 classes: owner, pet, tasks, and scheduler. The first 3 hold specific object data, and the scheduler class will be in charge of the planning using that data.

Owner and Pet are aggregation relationships.
Owner has pets. Pets have tasks.

**b. Design changes**

Yes, my design changed during implentation. The AI initially wanted to store a start_time, end_time, and duration. However, I decided to remove the end_time property, as we can simply calculate it from the other two properties.
It simplifies the class and prevents it from storing unnecessary data.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

My scheduler is greedy. It sorts tasks by priority and places each one if it fits in the time left. It never goes back to try a different combination, so it doesn't always use the owner's time as well as it could. For example, with 60 minutes, a 50-minute high-priority task and two 30-minute medium tasks, it schedules only the high-priority task and skips both medium ones. Doing the two medium tasks instead would fill the full hour.

I think this is reasonable for a pet owner because priority should win. If something is marked high priority, like meds or feeding, it should get done before lower-priority tasks, even if that means fewer tasks overall.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI tools for brainstorming the classes and refactoring the changes I want. I looked over each line of code and questioned the AI's implementation.
The prompts and questions that were most helpful involved asking for the purpose of the line of code and using my own knowledge to make it's implementations better. I also wanted to know the tradeoffs to make sure we don't go into scope creep.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
One suggestion I did not accept was using a list for uniqueness instead of a set. The AI was hesistant to change the mmd simply because it had a list type on a property, and it caused uniqueness to run in O(n). I made sure to change the implementation into a set.

- How did you evaluate or verify what the AI suggested?
By reading each line of code I understood and playing out the flow in my head. Then I verify what I understand as well as get explanations for the implementations I don't get.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
