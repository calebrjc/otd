package server

import "net/http"

func index(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(200)
	w.Write([]byte("Hello, World!"))
}

func registerRoutes() http.Handler {
	mux := http.NewServeMux()

	mux.HandleFunc("/", index)

	return corsMiddleware(mux)
}
