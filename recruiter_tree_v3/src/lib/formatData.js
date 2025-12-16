import { getRecruiters } from "@/db/database";
/* format recruiter data into a tree structure (parent with childrens)
    {
        name: "Pufikas",
        children: [...]
    }
*/

export async function formattedHierarchical(ignoreWithNoRecruiter = false) {
    // ignoreWithNoRecruiter, is a test and need more data with valid recruited_by
    const data = await getRecruiters();
    const roots = [];
    const byId = new Map(data.map(d => [d.id, {...d, children: [] }]));
    byId.forEach(node => {
        if (ignoreWithNoRecruiter == true && node.recruited_by === null) {
            return;
        }
        if (node.recruited_by && !ignoreWithNoRecruiter) {
            byId.get(node.recruited_by)?.children.push(node);
        } else {
            roots.push(node);
        }
    })
    
    return roots;
}