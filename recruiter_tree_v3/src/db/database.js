import { supabase } from "@/lib/supabaseClient";

export async function getRecruiters() {
  const { data } = await supabase
  .from('members')
  .select(`
    id,
    name,
    updated_at,
    recruited_by,
    recruiter:recruited_by(name)`
  ).order('id', { ascending: true })

  return data;
}

export async function getRecruiterData(id) {
  const { data } = await supabase
    .from('members')
    .select(`
      id,
      name,
      updated_at,
      recruited_by,
      recruiter:recruited_by(name)
    `)
    .eq('id', id)
    .single();

  return data;
}