const sb = supabase.createClient("https://ieypeyayioopenqlkkju.supabase.co", "sb_publishable_j2iWKMFDOH2L6Ou-QsFTqA_BnhLYNrW");
const login = () => sb.auth.signInWithOAuth({ provider: "google", options: { redirectTo: location.href } });
const logout = async () => { await sb.auth.signOut(); location.reload(); };
const getUser = async () => (await sb.auth.getSession()).data.session?.user;
const getToken = async () => (await sb.auth.getSession()).data.session?.access_token;

document.addEventListener("DOMContentLoaded", async () => {
  const btn = document.querySelector("#auth-btn");
  if (!btn) return;
  const user = await getUser();
  btn.textContent = user ? "Log out" : "Sign in with Google";
  btn.onclick = user ? logout : login;
});