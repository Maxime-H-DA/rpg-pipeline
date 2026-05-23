FROM gcc:13 AS compilation

WORKDIR /app
COPY rpg-source/ .
RUN g++ -std=c++17 -Wall -o rpg_game main.cpp

FROM debian:bookworm-slim

WORKDIR /app
COPY --from=compilation /app/rpg_game .
COPY --from=compilation /app/items.csv .
COPY --from=compilation /app/monsters.csv .

CMD ["./rpg_game"]