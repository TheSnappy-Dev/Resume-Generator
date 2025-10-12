package com.example.resumegenerator;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.ui.Model;

@Controller
public class ResumeController {

    @PostMapping("/resume")
    public String generateResume(
        @RequestParam String name,
        @RequestParam String email,
        @RequestParam String education,
        @RequestParam String experience,
        @RequestParam String skills,
        Model model
    ) {
        model.addAttribute("name", name);
        model.addAttribute("email", email);
        model.addAttribute("education", education);
        model.addAttribute("experience", experience);
        model.addAttribute("skills", skills.split(","));
        return "resume";
    }
}
