package main

import (
	"context"
	"log"
	"log/slog"
	"os"

	"github.com/urfave/cli/v3"
)

func main() {
	cmd := &cli.Command{
		Usage: "A server for managing and sending daily messages",
		Commands: []*cli.Command{
			{
				Name:  "run",
				Usage: "Run the OTD web and messaging server",
				Action: func(ctx context.Context, cmd *cli.Command) error {
					slog.Info("Running server...")
					runApp()

					return nil
				},
			},
		},
	}

	if err := cmd.Run(context.Background(), os.Args); err != nil {
		log.Fatal(err)
	}
}
