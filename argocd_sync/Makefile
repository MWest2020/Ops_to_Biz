UNIT_DIR := $(HOME)/.config/systemd/user
SERVICE  := argocd-sheets-sync.service
TIMER    := argocd-sheets-sync.timer

.PHONY: install uninstall run status logs

install:
	mkdir -p $(UNIT_DIR)
	cp systemd/$(SERVICE) $(UNIT_DIR)/$(SERVICE)
	cp systemd/$(TIMER)   $(UNIT_DIR)/$(TIMER)
	systemctl --user daemon-reload
	systemctl --user enable --now $(TIMER)
	@echo "Timer installed and started. Next run:"
	@systemctl --user list-timers $(TIMER) --no-pager

uninstall:
	systemctl --user disable --now $(TIMER) || true
	rm -f $(UNIT_DIR)/$(SERVICE) $(UNIT_DIR)/$(TIMER)
	systemctl --user daemon-reload
	@echo "Uninstalled."

run:
	systemctl --user start $(SERVICE)

status:
	systemctl --user status $(TIMER) $(SERVICE) --no-pager || true

logs:
	journalctl --user -u $(SERVICE) -n 50 --no-pager
