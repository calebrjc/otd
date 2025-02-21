package server

import (
	"fmt"
	"net/http"
	"time"
)

func New(port int) *http.Server {
	s := http.Server{
		Addr:         fmt.Sprintf(":%d", port),
		Handler:      registerRoutes(),
		IdleTimeout:  time.Minute,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 30 * time.Second,
	}

	return &s
}
