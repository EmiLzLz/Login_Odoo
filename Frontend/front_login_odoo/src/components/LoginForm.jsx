import React, { useEffect, useState } from "react";

function LoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userData, setUserData] = useState(null);
  const [activities, setActivities] = useState([]);
  const [loadingActivities, setLoadingActivities] = useState(false);

  //funcion para obtener actividades
  const fetchActivities = async () => {
    try {
      setLoadingActivities(true);
      const token = localStorage.getItem("token");
  
      const response = await fetch("http://localhost:8000/api/user-activities", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
  
      if (!response.ok) {
        throw new Error(`Error al cargar actividades: ${response.status}`);
      }
  
      let data;
      try {
        data = await response.json(); // Evitar error de JSON inválido
      } catch (error) {
        throw new Error("La respuesta del servidor no es un JSON válido");
      }
  
      setActivities(data);
    } catch (error) {
      console.error("Error de conexión o de datos: ", error);
    } finally {
      setLoadingActivities(false);
    }
  };

  //comprobar si hay token guardado
  useEffect(() => {
    const token = localStorage.getItem("token");
    const storedUserData = localStorage.getItem("userData");
  
    if (token && storedUserData) {
      try {
        setUserData(JSON.parse(storedUserData));
        setIsLoggedIn(true);
        fetchActivities();
      } catch (error) {
        console.error("Error al parsear userData:", error);
      }
    }
  }, []);

  const login = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
  
    try {
      const response = await fetch("http://localhost:8000/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
  
      let data;
      try {
        data = await response.json(); // Solo intenta parsear si la respuesta es válida
      } catch (err) {
        throw new Error("Respuesta del servidor inválida");
      }
  
      if (response.ok) {
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("userData", JSON.stringify(data.user));
        setUserData(data.user);
        setIsLoggedIn(true);
        console.log("Login exitoso", data);
      } else {
        setError(data.detail || "Error al iniciar sesión");
        console.error("Error de login", data.detail);
      }
    } catch (err) {
      setError("Error de conexión con el servidor");
      console.error("Error: ", err);
    } finally {
      setLoading(false);
    }
  };

  //funcion para cerrar sesion
  const logOut = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userData");
    setIsLoggedIn(false);
    setUserData(null);
  };

  //si el usuario esta logeado, mostrar su informacion
  if (isLoggedIn && userData) {
    return (
      <div className="dashboard">
        <div className="user-profile">
          <h2>Bienvenido</h2>
          <div className="user-details">
            <p>
              <strong>Nombre: </strong>
              {userData.name}
            </p>
            {userData.email && (
              <p>
                <strong>Correo: </strong>
                {userData.email}
              </p>
            )}
            {userData.role && (
              <p>
                <strong>Cargo: </strong>
                {userData.role}
              </p>
            )}
          </div>
          <button onClick={logOut} className="logout-button">
            Cerrar sesión
          </button>
        </div>

        <div className="activities-section">
          <h3>Actividades/Productos disponibles para vent</h3>

          {loadingActivities ? (
            <p>Cargando actividades...</p>
          ) : activities.length > 0 ? (
            <div className="activities-grid">
              {activities.map((activity) => (
                <div>
                  <h4>{activity.name}</h4>
                  {activity.description && <p>{activity.description}</p>}
                  {activity.list_price && <p>Precio: ${activity.list_price}</p>}
                  {activity.type && <p>Tipo: {activity.type}</p>}
                </div>
              ))}
            </div>
          ) : (
            <p>No hay actividades disponibles para tu cuenta</p>
          )}
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={login}>
      <label htmlFor="username">Username</label>
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <label htmlFor="password">Password</label>
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      {error && <div className="error-message">{error}</div>}
      <button type="submit">LOG IN</button>
    </form>
  );
}

export default LoginForm;
