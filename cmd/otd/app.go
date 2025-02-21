package main

import (
	"context"
	"fmt"
	"log/slog"
	"net/http"
	"os/signal"
	"syscall"

	"github.com/calebrjc/otd/internal/server"
)

func awaitShutdownSignal(shdn chan bool) {
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	// NOTE(Caleb): Block until the shutdown signal is received
	<-ctx.Done()

	slog.Info("Shutdown signal received")

	shdn <- true
}

func runApp() {
	slog.Info("Starting up...")

	server := server.New(5000)
	go func() {
		err := server.ListenAndServe()
		if err != nil && err != http.ErrServerClosed {
			panic(fmt.Sprintf("Failed to start server: %s", err))
		}
	}()

	shdn := make(chan bool, 1)
	go awaitShutdownSignal(shdn)
	<-shdn // NOTE(Caleb): Block until the shutdown signal is received

	slog.Info("Shutting down...")
}
