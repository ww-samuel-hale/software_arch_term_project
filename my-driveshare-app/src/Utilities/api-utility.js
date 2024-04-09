const baseURL = 'http://localhost:5000/';

async function get(endpoint) {
  const url = baseURL + endpoint;
  const response = await fetch(url, {
    method: 'GET',
    credentials: 'include',
  });
  if (response.ok) {
    return { status: response.status, data: await response.json() };
  } else {
    return { status: response.status, data: null };
  }
}

async function post(endpoint, data) {
  const url = baseURL + endpoint;
  try {
    const response = await fetch(url, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.ok
      ? await response.json()
      : new Error(`HTTP error! status: ${response.status}`);
  } catch (error) {
    console.error('Error posting data:', error);
    throw error;
  }
}

async function put(endpoint, data) {
  const url = baseURL + endpoint;
  try {
    const response = await fetch(url, {
      method: 'PUT',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.ok
      ? await response.json()
      : new Error(`HTTP error! status: ${response.status}`);
  } catch (error) {
    console.error('Error updating data:', error);
    throw error;
  }
}

async function deleteReq(endpoint) {
  const url = baseURL + endpoint;
  try {
    const response = await fetch(url, {
      method: 'DELETE',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.ok
      ? await response.json()
      : new Error(`HTTP error! status: ${response.status}`);
  } catch (error) {
    console.error('Error deleting data:', error);
    throw error;
  }
}

export { get, post, put, deleteReq };
