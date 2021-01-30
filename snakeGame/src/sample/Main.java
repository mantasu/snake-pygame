package sample;

import javafx.animation.AnimationTimer;
import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.canvas.Canvas;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.input.KeyCode;
import javafx.scene.input.KeyEvent;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.scene.text.Font;
import javafx.stage.Stage;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class Main extends Application {
    static int speed = 5;
    static int foodColor = 0;
    static int width = 20;
    static int height = 20;
    static Point food = new Point(0, 0);
    static int pointSize = 25;
    static List<Point> snake = new ArrayList<>();
    static Dir direction = Dir.left;
    static boolean gameOver = false;
    static Random rand = new Random();

    public enum Dir{
        left, right, up, down
    }

    public static class Point{
        int x;
        int y;

        public Point(int x, int y) {
            this.x = x;
            this.y = y;
        }
    }

    @Override
    public void start(Stage primaryStage) throws Exception{
        placeFood();

        VBox root = new VBox();
        Canvas canvas = new Canvas(width*pointSize, height*pointSize);
        GraphicsContext ctx = canvas.getGraphicsContext2D();
        root.getChildren().add(canvas);

        new AnimationTimer() {
            long lastTick = 0;

            public void handle (long now) {
                if(lastTick == 0) {
                    lastTick = now;
                    tick(ctx);
                    return;
                }
                if(now - lastTick > 1_000_000_000 / speed) {
                    lastTick = now;
                    tick(ctx);
                }
            }
        }.start();

        Scene scene = new Scene(root, canvas.getWidth(), canvas.getHeight());

        // Controls

        scene.addEventFilter(KeyEvent.KEY_PRESSED, key -> {
            switch(key.getCode()) {
                case UP:
                    direction = Dir.up;
                    break;
                case LEFT:
                    direction = Dir.left;
                    break;
                case DOWN:
                    direction = Dir.down;
                    break;
                case RIGHT:
                    direction = Dir.right;
                    break;
            }
        });

        snake.add(new Point(width/2, height/2));
        snake.add(new Point(width/2, height/2));
        snake.add(new Point(width/2, height/2));

        // scene.getStylesheets().add(getClass().getResource("application.css").toExternalForm());

        primaryStage.setTitle("Snake Game");
        primaryStage.setScene(scene);
        primaryStage.show();
    }

    // Tick
    public static void tick(GraphicsContext ctx) {
        if(gameOver) {
            ctx.setFill(Color.RED);
            ctx.setFont(new Font("", 50));
            ctx.fillText("GAME OVER", 100, 250);
            return;
        }

        // Move all body points to the last position of the body point in front
        for(int i = snake.size() - 1; i > 0; i--) {
            snake.get(i).x = snake.get(i-1).x;
            snake.get(i).y = snake.get(i-1).y;
        }

        // Move the head point
        switch(direction){
            case up:
                snake.get(0).y--;
                break;
            case down:
                snake.get(0).y++;
                break;
            case left:
                snake.get(0).x--;
                break;
            case right:
                snake.get(0).x++;
                break;
        }

        // Check for collision
        if(snake.get(0).y < 0 || snake.get(0).y > height || snake.get(0).x < 0 || snake.get(0).x > width) {
            gameOver = true;
        }

        for(int i = 1; i < snake.size(); i++) {
            if(snake.get(i).x == snake.get(0).x && snake.get(i).y == snake.get(0).y) {
                gameOver = true;
                break;
            }
        }

        // Eat food
        if(food.x == snake.get(0).x && food.y == snake.get(0).y) {
            snake.add(new Point(-1, -1));
            placeFood();
        }

        // Fill background
        ctx.setFill(Color.BLACK);
        ctx.fillRect(0, 0, width*pointSize, height*pointSize);

        // Score
        ctx.setFill(Color.WHITE);
        ctx.setFont(new Font("", 30));
        ctx.fillText("Score: " +(speed - 6), 10, 30);

        // Food color
        Color cc = Color.WHITE;

        switch(foodColor) {
            case 0:
                cc = Color.PURPLE;
                break;
            case 1:
                cc = Color.LIGHTBLUE;
                break;
            case 2:
                cc = Color.YELLOW;
                break;
            case 3:
                cc = Color.PINK;
                break;
            case 4:
                cc = Color.ORANGE;
                break;
        }

        ctx.setFill(cc);
        ctx.fillOval(food.x*pointSize, food.y*pointSize, pointSize, pointSize);

        // Draw snake
        for(Point p: snake){
            ctx.setFill(Color.LIGHTGREEN);
            ctx.fillRect(p.x*pointSize, p.y*pointSize, pointSize-1, pointSize-1);
            ctx.setFill(Color.GREEN);
            ctx.fillRect(p.x*pointSize, p.y*pointSize, pointSize-2, pointSize-2);
        }
    }

    // Food
    public static void placeFood() {
        start: while(true) {
            int x = rand.nextInt(width);
            int y = rand.nextInt(height);

            for (Point p : snake) {
                if (p.x == x && p.y == y) {
                    continue start;
                }
            }
            foodColor = rand.nextInt(5);
            speed++;

            food.x = x;
            food.y = y;

            break;
        }
    }


    public static void main(String[] args) {
        launch(args);
    }
}
