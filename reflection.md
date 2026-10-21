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

task completion, daily and weekly recurrence, priority sorting, time-budget fits, tasks that are too long for the remaining time, consecutive non-overlapping start times, and a shared schedule containing tasks for multiple pets.

Edge cases include an owner with no pets, a pet with no tasks, a task
that is not due yet, and invalid priorities, durations, and frequencies. Verified that schedule explanations mention matching pet needs and owner
preferences.

**b. Confidence**

My confidence level is 4 out of 5 stars. I am confident in the core scheduling
logic because every behavior currently covered by the automated suite passes,
including sorting, available-time limits, recurrence, and multi-pet scheduling.
I did not choose 5 stars because the Streamlit interface is not covered by
automated tests and there may be combinations of real user data that the unit
tests do not cover.

With more time, I would test schedules that cross midnight, owners with zero or
invalid available time, recurring tasks created without an initial due date,
and much larger task lists. I would also add tests that simulate the Streamlit
workflow, including adding pets and tasks, generating a plan, and displaying
the correct warning when tasks are skipped.

---

## 5. Reflection

**a. What went well**

I am most satisfied with the structure of the project and the design choices I made in code separation/combination, algorithmic simplicity, and complexity balancing.

**b. What you would improve**

Definitely the UX, a lot of the features could use dropdowns and other buttons to make everything easier and less type-heavy.

**c. Key takeaway**

AI is not good at designing systems and looking far ahead into a future of maintability and scalabilty for humans. While it can definitely produce algorithms well, it doesn't know how to make it readable and easy to change if needs update.
